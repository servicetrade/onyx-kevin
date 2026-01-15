import { useMemo, useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { useSettingsContext } from "@/components/settings/SettingsProvider";
import { NEXT_PUBLIC_DO_NOT_USE_TOGGLE_OFF_DANSWER_POWERED } from "@/lib/constants";
import { cn } from "@/lib/utils";
import Text from "@/refresh-components/texts/Text";

export const FOLDED_SIZE = 24;
const UNFOLDED_SIZE = 88;

export interface LogoProps {
  folded?: boolean;
  className?: string;
}

export default function Logo({ folded, className }: LogoProps) {
  const settings = useSettingsContext();
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Determine logo source - use static files when enterprise settings not configured
  const logoSrc = settings.enterpriseSettings?.use_custom_logo
    ? "/api/enterprise-settings/logo"
    : mounted && resolvedTheme === "dark"
      ? "/logo-dark.png"
      : "/logo.png";

  const logo = useMemo(
    () => (
      <img
        src={logoSrc}
        alt="Logo"
        style={{
          objectFit: "contain",
          height: FOLDED_SIZE,
          width: FOLDED_SIZE,
        }}
        className={cn("flex-shrink-0", className)}
      />
    ),
    [className, logoSrc]
  );

  const applicationName = settings.enterpriseSettings?.application_name || "Kevin AI";

  return folded ? (
    <img
      src={logoSrc}
      alt="Logo"
      style={{
        objectFit: "contain",
        height: FOLDED_SIZE,
        width: FOLDED_SIZE,
      }}
      className={cn("flex-shrink-0", className)}
    />
  ) : (
    <div className="flex flex-col">
      <div className="flex flex-row items-center gap-2">
        {logo}
        <Text
          headingH3
          className={cn("line-clamp-1 truncate", folded && "invisible")}
          nowrap
        >
          {applicationName}
        </Text>
      </div>
      {!NEXT_PUBLIC_DO_NOT_USE_TOGGLE_OFF_DANSWER_POWERED && (
        <Text
          secondaryBody
          text03
          className={cn(
            "ml-[33px] line-clamp-1 truncate",
            folded && "invisible"
          )}
          nowrap
        >
          Powered by Onyx
        </Text>
      )}
    </div>
  );
}
