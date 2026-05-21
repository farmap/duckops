import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';

const SERIES_COLORS = [
  '56, 189, 248',  // Cyan/Sky
  '52, 211, 153',  // Emerald/Mint
  '129, 140, 248', // Indigo/Purple
  '251, 146, 60',  // Orange/Amber
  '251, 113, 133', // Rose/Pink
];

interface MetricResponse {
  labels: string[];
  datasets: { label: string; data: number[]; unit: string }[];
}

export default function MetricsChart({ slug }: { slug: string }) {
  const [data, setData] = useState<MetricResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch from relative /api/ path which hits the Vite proxy we set up
    fetch(`/api/metrics/${slug}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(json => setData(json))
      .catch(e => setError(e.message));
  }, [slug]);

  if (error) {
    return (
      <div className="my-8 p-4 rounded-xl bg-rose-950/50 text-rose-200 font-mono text-sm border border-rose-800">
        Error loading metrics: {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="my-8 h-[400px] flex items-center justify-center text-slate-400 bg-slate-900/50 rounded-2xl border border-slate-800 animate-pulse">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p>Crunching DuckDB Parquet Data...</p>
        </div>
      </div>
    );
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc' },
      axisPointer: { type: 'cross', label: { backgroundColor: '#334155' } }
    },
    legend: {
      data: data.datasets.map(ds => ds.label || ''),
      textStyle: { color: '#94a3b8' },
      top: '0%',
      right: '4%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.labels.map(ts => {
        const d = new Date(ts);
        return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:00`;
      }),
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100
      },
      {
        start: 50,
        end: 100,
        borderColor: '#334155',
        fillerColor: 'rgba(56, 189, 248, 0.1)',
        handleStyle: { color: '#38bdf8' },
        textStyle: { color: '#94a3b8' },
        bottom: 0
      }
    ],
    series: data.datasets.map((ds, i) => {
      const rgbColor = SERIES_COLORS[i % SERIES_COLORS.length];
      return {
        name: ds.label,
        type: 'line',
        smooth: true,
        symbol: 'none',
        itemStyle: { color: `rgb(${rgbColor})` },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{
                offset: 0, color: `rgba(${rgbColor}, 0.2)`
            }, {
                offset: 1, color: `rgba(${rgbColor}, 0.0)`
            }]
          }
        },
        data: ds.data
      };
    })
  };

  return (
    <div className="my-8 p-6 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 shadow-2xl">
      <div className="flex items-center space-x-3 mb-2">
        <div className="w-3 h-3 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></div>
        <h3 className="text-xl font-semibold text-slate-100 m-0">Lakehouse Metrics</h3>
      </div>
      <p className="text-sm text-slate-400 mb-6 m-0">Zero-copy aggregation via DuckDB over raw Parquet</p>
      <ReactECharts option={option} style={{ height: '400px', width: '100%' }} />
    </div>
  );
}
