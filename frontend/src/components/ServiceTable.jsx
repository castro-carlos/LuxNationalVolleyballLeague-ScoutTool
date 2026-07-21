import React from 'react';

export const ServiceTable = ({ data }) => (
  <table className="w-full text-left border-collapse">
    <thead>
      <tr className="border-b border-slate-700 text-slate-400 text-sm">
        <th className="pb-3 font-semibold">Player Name</th>
        <th className="pb-3 font-semibold text-center">Total Serves</th>
        <th className="pb-3 font-semibold text-center text-emerald-400">Aces</th>
        <th className="pb-3 font-semibold text-center text-rose-400">Errors</th>
        <th className="pb-3 font-semibold text-center text-emerald-400">Ace %</th>
        <th className="pb-3 font-semibold text-right text-rose-400">Error %</th>
      </tr>
    </thead>
    <tbody className="divide-y divide-slate-700/50">
      {data.map((player, index) => (
        <tr key={index} className="hover:bg-slate-700/30 transition-colors">
          <td className="py-3 font-medium text-slate-200">{player.player_name}</td>
          <td className="py-3 text-center text-slate-400">{player.total_serves}</td>
          <td className="py-3 text-center text-emerald-400 font-medium">{player.aces}</td>
          <td className="py-3 text-center text-rose-400">{player.error_serves}</td>
          <td className="py-3 text-center text-emerald-400 font-semibold">{Number(player.service_efficiency).toFixed(1)}%</td>
          <td className="py-3 text-right text-rose-400 font-semibold bg-rose-500/5 px-2 rounded">
            {Number(player.service_error_rate).toFixed(1)}%
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);