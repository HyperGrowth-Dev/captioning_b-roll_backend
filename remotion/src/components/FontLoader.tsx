import { loadFont as loadBarlow } from "@remotion/google-fonts/Barlow";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { continueRender, delayRender } from "remotion";
import { useEffect, useState } from "react";

export const FontLoader: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [handle] = useState(() => delayRender());

  useEffect(() => {
    const loadFonts = async () => {
      await Promise.all([
        // Load Barlow font family
        loadBarlow("normal", {
          weights: ["900"]
        }),
        // Load Montserrat as fallback
        loadMontserrat(),
      ]);
      continueRender(handle);
    };

    loadFonts();
  }, [handle]);

  return <>{children}</>;
}; 