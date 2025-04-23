const chromium = require('@sparticuz/chromium');
const puppeteer = require('puppeteer-core');
const { bundle } = require('@remotion/bundler');
const { getCompositions, renderMedia } = require('@remotion/renderer');
const path = require('path');

let browser = null;
let page = null;

async function closePage() {
  try {
    if (page) {
      const client = await page.target().createCDPSession();
      await client.detach();
      await page.close().catch(() => {
        console.log('Page was already closed');
      });
      page = null;
    }
  } catch (error) {
    console.log('Error while closing page:', error.message);
    // Don't throw the error, just log it
  }
}

exports.handler = async (event, context) => {
  try {
    // Initialize browser if not exists
    if (!browser) {
      browser = await puppeteer.launch({
        args: chromium.args,
        defaultViewport: chromium.defaultViewport,
        executablePath: await chromium.executablePath(),
        headless: chromium.headless,
        ignoreHTTPSErrors: true,
      });
    }

    // Create a new page
    page = await browser.newPage();

    // Bundle the Remotion project
    const bundled = await bundle({
      entryPoint: path.join(__dirname, '../remotion/src/compositions/Root.tsx'),
      webpackOverride: (config) => {
        return {
          ...config,
          resolve: {
            ...config.resolve,
            extensions: ['.tsx', '.ts', '.js'],
          },
        };
      },
    });

    // Get the composition
    const compositions = await getCompositions(bundled);
    const composition = compositions.find((c) => c.id === 'CaptionVideo');

    if (!composition) {
      throw new Error('Could not find CaptionVideo composition');
    }

    // Render the video
    await renderMedia({
      composition,
      serveUrl: bundled,
      codec: 'h264',
      outputLocation: event.outputPath,
      inputProps: event.inputProps,
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Success' })
    };

  } catch (error) {
    console.error('Error in Lambda function:', error);

    // Always try to close the page on error
    await closePage();

    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  } finally {
    // Keep browser open for warm starts
    // but make sure page is closed
    if (page) {
      await closePage();
    }
  }
}; 