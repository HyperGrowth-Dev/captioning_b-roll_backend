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
          videoSrc: "https://hyper-editor.s3.us-east-2.amazonaws.com/input/292edd91-b232-41c7-8c79-c054c5193af3.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBgaCXVzLWVhc3QtMiJGMEQCIB%2BhbNMU%2F6HPOzCQaO8M%2Bp0JNxtnZMLSdrJ8kOLxTIWcAiAyxKM9YLx4ix806PB6wLIR4WEIXrpa0qkZuqQjQ9hfsiq%2BAwix%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDg4ODU3NzA0MzAwMyIMH4xiK6YfTOXmftEJKpIDloxrpqxKd0DpO8rjjVEXi6cK1rVb2lHq9hiHX5F6g4NUmQguZGmbMsljKFcoRPtrE9CfFzVb4bvKxfr%2F3Dv1xZ%2BtCJMJd3bwz0H6AzOZAfxhBOLW2lIeUOPwLWUPF24Zv1s4eu2DqQLtORGfH5%2F0wPitU0hsfvCtUDhAjt0abRJmd1JquAuJOtG4yQPlBxCC8C6oL35bogd73Zlq9yzKGjr3hyY0l2J%2BG4JNlB1lY%2Fasi3szyiJ%2F5XMVoK7%2BnazL6HAoajDqCpC1iw2yxOQLSLfVpGnP%2FxOCPfFs71MA%2BgB6GU2RLV%2F6gdKmeU150K08p%2FXL5cv1ibI3mM1ULfqNm6ZsBEprckwAc0V%2BjtRzpdDflLB5ZecivMDDWgjVd5v8WzUsAKNUcNHA8u4m9NDdHfZqR5AuOOGoNBW9vDOF6pgd2cYCPeNys7rAX4Uv7KSQCdDnr6rSVVPL4xVg27of5GkG90G%2FKyd%2BAmiUv3W172TiYAjRJiLprUBCLLxohtPlC7EHPhV9XUcBMJzyTSDpKptdMOCTycAGOt8CSYsBcZzzLLq4gVtFkcJqZOMYeEli8KYBlY3MYJXtPtA6GM8TwTFgKQt5z1mu%2FDW8LpJBFpZSR5hxoVFilJYYN3nN%2BoAstApTKdmvghMmPIMNnLCuXJ28xG4PqJLL1bTNeUzo4h3xUHR2%2Bnk0hwK8i4RIB0vFXUI%2FpFh6WzOwuY4Z5YnMl4uOYFEx9sR7fnhlmsbV3YcQvICeCowrogi1KvNDUa8G9yQPpukPQs5kiMjfTbnZeWha3MRQ5gewLFjqSL6hHZ3w5weyTIWgGUxhfTGA5hIXgp8YAhqdqyiDrqneFRlXD7kdvnWtSc%2FSu2sWO%2FygTwAmohOO701TMNoC1m%2BCepSOxIPKTSwhZ5bvyjFreIZjlNWWaXd9CYTIbpcFYv7M0PBk04LgOcyBz29h%2BifzGIh3s3CWYqScCoiW6wQ2yHSx%2FbE8nMN4e0oW4Xhnk%2BtuT8bVxdHQ1ZC6P2BU&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA45Y2RVI5VDCJVIRZ%2F20250430%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250430T233817Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=06e2109cdc1b712e04f34a09481b471e3abaa85cebf0dce72e1eff981f7c7ea4",
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