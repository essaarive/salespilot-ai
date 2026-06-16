import type { ReactNode } from "react";

interface DataTableProps<T> {
  columns: Array<{
    key: string;
    title: string;
    render: (row: T) => ReactNode;
  }>;
  data: T[];
  emptyText?: string;
}

export default function DataTable<T>({ columns, data, emptyText = "暂无数据" }: DataTableProps<T>) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="whitespace-nowrap px-4 py-3 text-left font-medium text-slate-600"
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.length === 0 ? (
              <tr>
                <td className="px-4 py-8 text-center text-slate-500" colSpan={columns.length}>
                  {emptyText}
                </td>
              </tr>
            ) : (
              data.map((row, index) => (
                <tr key={index} className="hover:bg-slate-50">
                  {columns.map((column) => (
                    <td key={column.key} className="max-w-xs px-4 py-3 align-top text-slate-700">
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
