import React from 'react';

export const AttackTable = ({ data }) => (
  <table className="w-full text-left border-collapse">
    <thead>
      <tr className="border-b border-slate-700 text-slate-400 text-sm">
        <th className="pb-3 font-semibold">Player Name</th>
        <th className="pb-3 font-semibold text-center">Total Spikes</th>
        <th className="pb-3 font-semibold text-center text-emerald-400">Kills</th>
        <th className="pb-3 font-semibold text-center text-rose-400">Errors</th>
        <th className="pb-3 font-semibold text-center text-purple-400">Blocked</th>
        <th className="pb-3 font-semibold text-right text-emerald-300">Efficiency %</th>
      </tr>
    </thead>
    <tbody className="divide-y divide-slate-700/50">
      {data.map((player, index) => (
        <tr key={index} className="hover:bg-slate-700/30 transition-colors">
          <td className="py-3 font-medium text-slate-200">{player.player_name}</td>
          <td className="py-3 text-center text-slate-400">{player.total_attacks}</td>
          <td className="py-3 text-center text-emerald-400 font-medium">{player.attack_kills}</td>
          <td className="py-3 text-center text-rose-400">{player.attack_errors}</td>
          <td className="py-3 text-center text-slate-500">{player.attack_blocked}</td>
          <td className="py-3 text-right text-emerald-400 font-bold bg-emerald-500/5 px-2 rounded">
            {Number(player.attack_efficiency).toFixed(1)}%
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);