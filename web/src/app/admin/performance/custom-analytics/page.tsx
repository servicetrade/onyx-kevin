"use client";

import React from "react";
import { AdminPageTitle } from "@/components/admin/Title";
import { FiBarChart2 } from "react-icons/fi";
import { Callout } from "@/components/ui/callout";

export default function Page() {
  return (
    <main className="pt-4 mx-auto container">
      <AdminPageTitle
        title="Custom Analytics"
        icon={<FiBarChart2 size={32} />}
      />

      <div className="mt-6">
        <p className="mb-8 text-lg">
          This page allows you to view and manage custom analytics settings for
          your Onyx instance.
        </p>

        <div className="mt-4">
          <Callout type="warning" title="Custom Analytics Information">
            Custom analytics allows you to integrate third-party analytics tools
            with Onyx. Contact your administrator for more information about
            setting up custom analytics for your organization.
          </Callout>
        </div>
      </div>
    </main>
  );
}
