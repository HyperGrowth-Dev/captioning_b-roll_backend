import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');
Config.setCrf(18);
Config.setPixelFormat('yuv420p');
Config.setAudioCodec('aac');
Config.setAudioBitrate('128k');
Config.setConcurrency(4);
Config.setOutputLocation('out');

Config.setBrowserExecutable('/usr/bin/google-chrome-stable');

// Lambda Configuration
Config.overrideWebpackConfig((currentConfiguration) => {
  return {
    ...currentConfiguration,
    target: 'node',
    externals: {
      'aws-sdk': 'aws-sdk',
    },
  };
}); 