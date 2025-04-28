import React, { useMemo } from "react";
import { useChatSessionGroups } from "@/app/ee/admin/performance/lib";
import { DateRangePickerValue } from "@/app/ee/admin/performance/DateRangeSelector";
import {
  ChartData,
  GroupingType,
} from "@/app/ee/admin/performance/usage/types";
import { ThreeDotsLoader } from "@/components/Loading";
import { ErrorCallout } from "@/components/ErrorCallout";
import { Card, CardContent } from "@/components/ui/card";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend,
} from "recharts";

const COLORS = [
  "#8884d8",
  "#83a6ed",
  "#8dd1e1",
  "#82ca9d",
  "#a4de6c",
  "#d0ed57",
  "#ffc658",
  "#ff8042",
  "#ff6361",
  "#bc5090",
];

export function ChartVisualizer({
  timeRange,
  groupingType,
  chartType,
}: {
  timeRange: DateRangePickerValue;
  groupingType: GroupingType;
  chartType: "bar" | "pie";
}) {
  const { data, error, isLoading } = useChatSessionGroups(
    timeRange,
    groupingType
  );

  const chartData: ChartData[] = useMemo(() => {
    if (!data) return [];

    return data.data.slice(0, 10).map((item) => ({
      name: item.name,
      value: item.count,
    }));
  }, [data]);

  if (error) {
    return (
      <ErrorCallout
        errorTitle="Error fetching chat session data"
        errorMsg={error?.message}
      />
    );
  }

  if (isLoading) {
    return <ThreeDotsLoader />;
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-lg text-muted-foreground">
          No data available for the selected time range.
        </p>
      </div>
    );
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === "bar" ? (
              <BarChart data={chartData}>
                <XAxis
                  dataKey="name"
                  tickFormatter={(value) => {
                    return value.length > 15
                      ? `${value.substring(0, 15)}...`
                      : value;
                  }}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" name="Chat Sessions">
                  {chartData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            ) : (
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                >
                  {chartData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [`${value} sessions`, "Count"]}
                />
                <Legend />
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
