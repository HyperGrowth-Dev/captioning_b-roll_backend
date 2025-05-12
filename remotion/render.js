import {
    renderMediaOnLambda,
    getRenderProgress
  } from '@remotion/lambda';
  
  const main = async () => {
    const render = await renderMediaOnLambda({
      serveUrl: 'https://remotionlambda-useast2-bvf5c7h3eb.s3.us-east-2.amazonaws.com/sites/caption-video/index.html',
      functionName: 'remotion-render-4-0-272-mem2048mb-disk2048mb-120sec',
      composition: 'CaptionVideo',
      inputProps: {
        videoSrc: 'https://hyper-editor.s3.us-east-2.amazonaws.com/input/292edd91-b232-41c7-8c79-c054c5193af3.mp4',
        captions: [], // TODO: replace with actual captions
        font: 'Barlow',
        fontSize: 48,
        color: 'white',
        position: 'bottom',
        highlightType: 'background'
      },
      codec: 'h264',
      imageFormat: 'jpeg',
      jpegQuality: 80,
      fps: 30,
      width: 1080,
      height: 1920,
      outName: 'your-rendered-video.mp4',
      bucketName: 'hyper-editor',
      privacy: 'public'
    });
  
    console.log('🟢 Render started!');
    console.log('🆔 Render ID:', render.renderId);
    console.log('📦 Bucket:', render.bucketName);
  
    // Track progress
    let done = false;
    while (!done) {
      const progress = await getRenderProgress({
        functionName: 'remotion-render-4-0-272-mem2048mb-disk2048mb-120sec',
        renderId: render.renderId,
        bucketName: render.bucketName
      });
  
      if (progress.fatalErrorEncountered) {
        console.error('❌ Fatal render error:', progress.errors);
        break;
      }
  
      if (progress.done) {
        done = true;
        console.log('✅ Render complete!');
        console.log('📁 Output key:', progress.outKey);
        console.log('🌐 Public URL:', progress.bucketUrl);
        break;
      }
  
      const pct = (progress.overallProgress ?? 0) * 100;
      console.log(`⏳ Progress: ${pct.toFixed(2)}% (${progress.renderedFrames} frames)`);
  
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  };
  
  main().catch((err) => {
    console.error('❌ Unexpected failure:', err);
  });
  