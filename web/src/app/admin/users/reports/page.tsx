"use client";

import React, { useState } from "react";
import { AdminPageTitle } from "@/components/admin/Title";
import { DateRangeSelector } from "@/app/ee/admin/performance/DateRangeSelector";
import { UsersIcon } from "@/components/icons/icons";
import { useTimeRange } from "@/app/ee/admin/performance/lib";
import { ChatSessionsReportTable } from "./ChatSessionsReportTable";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import CardSection from "@/components/admin/CardSection";
import { Separator } from "@/components/ui/separator";
import { GroupingType } from "@/app/ee/admin/performance/usage/types";
import { ChartVisualizer } from "./ChartVisualizer";

export default function ChatSessionsReportPage() {
  const [timeRange, setTimeRange] = useTimeRange();
  const [groupingType, setGroupingType] = useState<GroupingType>("user");
  const [chartType, setChartType] = useState<"bar" | "pie">("bar");

  return (
    <main className="pt-4 mx-auto container">
      <AdminPageTitle
        title="Chat Sessions Report"
        icon={<UsersIcon size={32} />}
      />

      <CardSection className="mt-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-end">
          <div>
            <h3 className="font-medium mb-2">Date Range</h3>
            <DateRangeSelector
              value={timeRange}
              onValueChange={(value) => setTimeRange(value as any)}
            />
          </div>

          <div>
            <h3 className="font-medium mb-2">Group By</h3>
            <RadioGroup
              value={groupingType}
              onValueChange={(value) => setGroupingType(value as GroupingType)}
              className="flex gap-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="user" id="user" />
                <Label htmlFor="user">User</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="assistant" id="assistant" />
                <Label htmlFor="assistant">Assistant</Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <h3 className="font-medium mb-2">Chart Type</h3>
            <RadioGroup
              value={chartType}
              onValueChange={(value) => setChartType(value as "bar" | "pie")}
              className="flex gap-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="bar" id="bar" />
                <Label htmlFor="bar">Bar Chart</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="pie" id="pie" />
                <Label htmlFor="pie">Pie Chart</Label>
              </div>
            </RadioGroup>
          </div>
        </div>

        <Separator className="my-4" />

        <ChartVisualizer
          timeRange={timeRange}
          groupingType={groupingType}
          chartType={chartType}
        />

        <Separator className="my-4" />

        <ChatSessionsReportTable
          timeRange={timeRange}
          groupingType={groupingType}
        />
      </CardSection>
    </main>
  );
}
