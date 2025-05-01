import { Composition } from 'remotion';
import CaptionVideo, { CaptionVideoPropsSchema } from './CaptionVideo';

const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="CaptionVideo"
        component={CaptionVideo}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        schema={CaptionVideoPropsSchema}
        defaultProps={{
          videoSrc: "https://hyper-editor.s3.us-east-2.amazonaws.com/input/292edd91-b232-41c7-8c79-c054c5193af3.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjECkaCXVzLWVhc3QtMiJIMEYCIQDtU0dPxLr4jl4p5FG3G94GLqoltmwaipWDOhfFK6jmXQIhAKaEhxP4M68FBcjie396yE69q7aziMMD3NEokmK234HjKr4DCML%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMODg4NTc3MDQzMDAzIgzcy91uC61B7jwRFi4qkgO1SC99awjTMcJw6LRmJk8oTuVZtX9ad%2FDyeyJLz4wt3TiJWpT8YMjveN%2B3%2B7GlEHDGjajwqSbl1uNULzG2koKHWBaDP6yGc%2B%2FDWoUIW77cEpZCHZrbqgoEjwE5JuEmnQe7wgtP9FcSnXIOrXYekatThu9%2BFVj8kYfd1MxUdL5QGYeUWqDIEBSWod2kbfjoOYvxpnzKcyLl0zEH4MpNKcFtWbohvPeYOM3MJaArQ1aE45zOpgoZLs8VO%2FizyHxCgSVOgTd2uzwU3zskBLFGF1RG9YlPnNtVvOkeKMdFpBvxl%2FoFwiM5SIyqvLssAmKLQbaEs6ZBFj2RqQI9fhoDHfMSvVkg60LyPe1o%2BKOfbQZrlAqUDeG9qZVR8fcCXzbZpBQR20ZDpHJ9hSbeYkCZgJ%2FrD5Z2XwzLvH9kyfRopidFP71GWVAn5xWfp3BXr%2BYDF0s30PuWnXI1USqgiexnsOkci3QzdUSRp2Ld4C9vbNkGQCnZBzdD4vxk8tTBegRp%2BQgDttD5V5afqkN2%2FH%2B2IaPOUtsw5sXOwAY63QIHpZU1A256LNQFYM9%2Fw2Vix94bhDWBh8d3qscJ2iZ87wegiDW15b2ggCyVHpt%2F9uYDYfxSfjBuNJ417JW1dCj%2FyU2oVFTRu7ElXQU2pmf75h0e9sVPIEAoN%2FOr0RYoU3bfFWdpLArSAVyc30IJsijHksxM9GcM48%2FqsSs3Nt8AWgdeh43P6O2Vj5tsCni26Kcxoo7ep6WVxmKFMZTwLDKiejIVCKb%2BfRMPMKR4jpoD4X%2FgD9nhYK5PpLfmMif3CsmsvSRoV%2Bp3VYBsfTEg9iZjm2kNkM89%2Bnwrp%2BoSjq%2BTMGtCo2OHJA5Pmshz2ZYM1WSmtljV3g2ilPb7VtaIyapYPiIReK9opUoL1GGhBBPJJpoIkHmGpWHkRlqHUCR6opHo%2BLbt%2Bsa1K9jtflTTYPE1ckE61d7hh8VyHP2yJ7EsnWHVfM0k0d2KMDgzzod5vHJSV3BYvJ1cAPhMx77A&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA45Y2RVI5WMJTFG2P%2F20250501%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250501T163928Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=6b26147a33ad86f089a3905910ca4b2095e00c5759a7e5a11f0c53b523d3eb3e",
          captions: [
            {
              text: "This is a test caption",
              startFrame: 0,
              endFrame: 90
            },
            {
              text: "Another caption appears here",
              startFrame: 150,
              endFrame: 240
            },
            {
              text: "Final test caption",
              startFrame: 300,
              endFrame: 390
            }
          ],
          font: "Montserrat-Bold",
          fontSize: 48,
          color: "white",
          position: "bottom",
          highlightType: "background"
        }}
      />
    </>
  );
};

export default RemotionRoot; 