import { Composition } from 'remotion';
import CaptionVideo, { CaptionVideoPropsSchema } from './CaptionVideo';
import { FontLoader } from '../components/FontLoader';
import { z } from 'zod';

const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="CaptionVideo"
        component={(props: z.infer<typeof CaptionVideoPropsSchema>) => (
          <FontLoader>
            <CaptionVideo {...props} />
          </FontLoader>
        )}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        schema={CaptionVideoPropsSchema}
        defaultProps={{
          videoSrc: "https://hyper-editor.s3.us-east-2.amazonaws.com/input/292edd91-b232-41c7-8c79-c054c5193af3.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMiJHMEUCIBzmvZKzXLolaEKWZXbxZem6aU3X8o42Lzv3Ds1m5w%2B7AiEA8%2Bt6YQrLhZSNItKZ%2F18%2F8zxiJZfvWUH3CFa5%2BhpJo4oquQMINBAAGgw4ODg1NzcwNDMwMDMiDIShzlor52gh8ckpdyqWA9Siy%2BwgoBgfaOKD4oY7fW%2BP1zMkOlPhlKwt8%2FVr3MRdPi4C2Ebf0IhZ0Ltqa%2BDHBYGlGMmJZzM8FzYeSapJX%2Bkgy7HSeDpJH4P6I6qIjukAAzjWM8l64Ah%2BJNw%2FrEzbYeGrbY1jstXMY2RjVy6%2BzOTknAx9JtWYeCe15I1O8GMvpOfel94iGh%2B7lzHEGJaKCvfjZeDx5i8sGeF1NkaaB6awUpNOH%2FARieLcYwODP5p22SaWWVx2qoemLcoFH8826eI1IjMkKACMh0P9tiV30YQfBkjmaDRzqPFKgn4e%2BxazwoxenGbS6Y2%2Ft8m1E%2BTzyxKNm6Jhz7p0QGKubpPticJZEps1%2FfrbEGbYx2GF%2FqZ9%2B2eVXYYrXRRpUWBbuTue3by%2BO1WlbCq1OEkIiF5Sv%2FRcqmSCyUtc3iD9lPhOEkMQQKbDyOw7fEXeYjxjjcwbubDeB4ejBLSepms61EjQqwb2ipX00vhad2Nx3kfXKGdRT3G24M072UlV6j1LjwlfnnymYsJEulS4F%2BhruXVzRYKkkwnx2kAwi5fkwAY63gJJ9DzMa8yRZGrm3GcgNCb1hPSek4BfwrMbcRJAoibH89E6gi5HfKlqnyrCDbhdirA%2FNPXWDDCgYoMuW%2Fpstkc598Ngzn97ebq3oxUVlMKfC5aoXLNgNPwY1LxGWFoazKnI3JQ%2B2M16lCntXCKgW7oALg%2BkRMj1EhHRVF%2BQq4FESIcFBZ970xNbJIooDcPMBh%2FvEldqJguLCMUUhth04kVv%2FydYwzfzzB18dtXeISc17ni%2BFXBqOmG36ZXC8Ojjtz1JWYyZG%2F6pHf7Q5RBY%2Bd34pfkPeC0mfR7m%2FdnPbB7sKaozxXxWIRvLpdU0DlGvFWa2FyWHvaQ0hRbFf5iQZ63IPjdea40GHCRbmHlrlY77PcxtGZO9%2BgsPvJ0CjJwzTxsS8IP7CiQCd2WUHnG2PJJUYwKjobc8CwA%2Bhz6xAf12oNeXWFH8qEqI1%2FbhlGAS%2FgDeJNTxAehoMmKM9AT1Vw%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA45Y2RVI5Q34QSA73%2F20250505%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250505T191116Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=97d3e65c2c0887563a4ebedf07f50440f8070a8aeb81f9465d565dce513e07fe",
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
          font: "Barlow-BlackItalic",
          fontSize: 48,
          color: "white",
          position: "bottom" as const,
          highlightType: "background" as const
        }}
      />
    </>
  );
};

export default RemotionRoot; 