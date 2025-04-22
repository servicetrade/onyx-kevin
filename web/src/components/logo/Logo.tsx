"use client";

import { useContext } from "react";
import { useTheme } from "next-themes";
import { SettingsContext } from "../settings/SettingsProvider";

export function Logo({
  height,
  width,
  className,
  size = "default",
}: {
  height?: number;
  width?: number;
  className?: string;
  size?: "small" | "default" | "large";
}) {
  const settings = useContext(SettingsContext);
  const { resolvedTheme } = useTheme();

  const sizeMap = {
    small: { height: 24, width: 22 },
    default: { height: 32, width: 30 },
    large: { height: 48, width: 45 },
  };

  const { height: defaultHeight, width: defaultWidth } = sizeMap[size];
  height = height || defaultHeight;
  width = width || defaultWidth;

  if (
    !settings ||
    !settings.enterpriseSettings ||
    !settings.enterpriseSettings.use_custom_logo
  ) {
    return (
      <div style={{ height, width }} className={className}>
			<img
				src={resolvedTheme === "dark" ? "/logo-dark.png" : "/logo.png"}
				alt="Logo"
				style={{ objectFit: "contain", height, width }}
			/>
      </div>
    );
  }

  return (
    <div
      style={{ height, width }}
      className={`flex-none relative ${className}`}
    >
      {/* TODO: figure out how to use Next Image here */}
      <img
        src="/api/enterprise-settings/logo"
        alt="Logo"
        style={{ objectFit: "contain", height, width }}
      />
    </div>
  );
}

export function LogoType({
  size = "default",
}: {
  size?: "small" | "default" | "large";
}) {
  const { resolvedTheme } = useTheme();
  
  return (
    <img
		src={resolvedTheme === "dark" ? "/logotype-dark.png" : "/logotype.png"}
		alt="Logo"
		style={{ objectFit: "contain" }}
		className="items-center w-full"
    />
  );
}
