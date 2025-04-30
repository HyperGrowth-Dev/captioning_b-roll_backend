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
          videoSrc: "https://hyper-editor.s3.us-east-2.amazonaws.com/input/292edd91-b232-41c7-8c79-c054c5193af3.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBMaCXVzLWVhc3QtMiJGMEQCICF7CU2VjlzepsmqFY6BLBu%2F6iCYl2HTcBGGhKGeBcoEAiAIwjdQzMtsvAvsJPjpxQcCPFdhZ4XeoaAHFmXLq42vgyq%2BAwis%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDg4ODU3NzA0MzAwMyIMCb9XA7Cj4ZNoO2YrKpIDLxwiu1IKC2JYkOH%2ByJOR1bcqpNeI%2BTqFBASU%2BL8TH4PoAakub55G1WLLSu8QW4w%2F9DH8VvW5qPnUtf8s6K8IiDd32nqoZwOZQmCCLpgLUzbGv1L3waSSpXGXeJ%2FnbuLdoXsF657MGT3zjyMzcTJs8CVVCVD695pTDJJEp%2BeOzdfeIIpKoICvingXCAUWbwRGZr7E9iMRsVonGQW1uNGXKLBTH5ORQp%2BcMCZ%2F6iz0sQkdD%2B3F%2Fv3yW4BP0aAELx5ze65R12Ho9LMqJrum1ItsHn%2F3CS88hqUofrLrlMh3ggU%2FJPsQRnkwfb7NxCctq%2BT3dkeQxdo3FWLtIsiSC9g%2Fj3MbeFN4zpMdLxv%2Fsx%2Fjy8aoTSHZroyJ0Lu1Tc%2FOoKvEcC9o4c%2FXQikaK6%2B%2BMB3Ie4DCjQNpnIbcs1dSx%2F7hRtY7P4cZYHXTW60dDPxhIMk7bv3S55nUmLUWHa1%2FUqO34ANeozRRaz3DSXzn%2BmOP8QoPbyZpaXWsVl04YJVVDQVmD%2BKOuqwayr%2FOb8xK4csY4WA0MOCTycAGOt8C%2BY%2F8KJz6pAaGNTavvM7QER2chL5rBv4dnHIW57JIQHYk3onMM6rwzwFyi9XD8mUZHiGsnUZbAkgsQSRbvT1WOzOnNvY0opE7HHIKUs9zNpnmVe9kFrrK8ujB%2FqUxwXc10yMmooYVgnuBxKMm2dVA%2BZ3Tv3JBWz56YnGXmhTdsFziQv2c%2FrwAUcMWWME9EZqeFk8JLz%2F3S2v2p%2BHSt%2BrxEooEiulRJBNXyRevc7PVf4TvD9rdMc5ocn0SqyH8Zp7NX8gzaMCukoXT4Shu9SXbFBv0hcQzdPxZaZTCMy6jDZ5U5dCpA%2FQLXUh6gPKecOpaWSz82q%2F2HdkoO%2BiNjbFTF1w%2BYCt9QaApLC%2BEVM0r%2BExWDudoBgvP1QoqC9BsjoRJYQISZ1%2BWqHiXlPlsAnvkliw5loytHH6x4b%2FA02tiZMnkUcsdyXtOqv9%2BjSqjfw9jU6fUDtzcMaA1Ezi%2Fzz13&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA45Y2RVI5VJCL5TIC%2F20250430%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250430T185939Z&X-Amz-Expires=10800&X-Amz-SignedHeaders=host&X-Amz-Signature=4dfa608269e0c7b9bb9f547eae02e6ec0e1e6ee3be39630a716f306d76f9b437",
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