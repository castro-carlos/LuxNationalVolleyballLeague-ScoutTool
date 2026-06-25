import React, { useState, useEffect } from 'react';

function App() {
  // State management for our data pipelines
  const [teams, setTeams] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('reception');

  // 1. Fetch all teams from your local FastAPI backend on mount
  useEffect(() => {
    fetch('http://localhost:8000/teams')
      .then((res) => res.json())
      .then((data) => setTeams(data))
      .catch((err) => console.error("Error fetching teams:", err));
  }, []);

  // 2. Fetch the reception leaderboard whenever the selected team changes
  useEffect(() => {
    if (!selectedTeamId) {
      setLeaderboard([]);
      return;
    }

    setLoading(true);
    fetch(`http://localhost:8000/teams/${selectedTeamId}/reception-scout`)
      .then((res) => res.json())
      .then((data) => {
        setLeaderboard(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching leaderboard:", err);
        setLoading(false);
      });
  }, [selectedTeamId]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      <header className="border-b border-slate-800 pb-4 mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-emerald-400">
          Luxembourg National Volleyball League
        </h1>
        <p className="text-slate-400 mt-1">Scout & Match Analytics Tool</p>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Side: Team Selector Controls */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl h-fit">
          <h2 className="text-xl font-semibold mb-4 text-emerald-300">Filters</h2>

          <label className="block text-sm font-medium text-slate-400 mb-2">
            Select Active Team
          </label>
          <select
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:outline-none focus:border-emerald-500"
            value={selectedTeamId}
            onChange={(e) => setSelectedTeamId(e.target.value)}
          >
            <option value="">-- Choose a Team --</option>
            {teams.map((team) => (
              <option key={team.id} value={team.id}>
                {team.team_name}
              </option>
            ))}
          </select>
        </div>

        {/* Right Side: Main Stats Displays */}
        <div className="md:col-span-2 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
          {/* Tab Navigation */}
          <div className="flex border-b border-slate-700 mb-6">
            <button
              onClick={() => setActiveTab('reception')}
              className={`pb-3 px-4 font-medium text-sm transition-colors ${
                activeTab === 'reception'
                  ? 'border-b-2 border-emerald-400 text-emerald-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Reception Errors Leaderboard
            </button>
            <button
              onClick={() => setActiveTab('general')}
              className="pb-3 px-4 font-medium text-sm text-slate-500 cursor-not-allowed"
              disabled
            >
              Other Metrics (Future Extension)
            </button>
          </div>

          {/* Conditional Rendering of Leaderboard Data */}
          {!selectedTeamId ? (
            <div className="text-center py-12 text-slate-500">
              Select a team from the filters sidebar to generate the scouting report.
            </div>
          ) : loading ? (
            <div className="text-center py-12 text-emerald-400 font-medium">
              Running SQL aggregations on Neon Cloud...
            </div>
          ) : leaderboard.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              No roster stats matched the minimum requirements for this team this season.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-700 text-slate-400 text-sm">
                    <th className="pb-3 font-semibold">Player Name</th>
                    <th className="pb-3 font-semibold text-center">Total Receptions</th>
                    <th className="pb-3 font-semibold text-center">Reception Errors</th>
                    <th className="pb-3 font-semibold text-right text-emerald-300">Error % (Worst First)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {leaderboard.map((player, index) => (
                    <tr key={index} className="hover:bg-slate-700/30 transition-colors">
                      <td className="py-3 font-medium text-slate-200">{player.player_name}</td>
                      <td className="py-3 text-center text-slate-400">{player.total_receptions}</td>
                      <td className="py-3 text-center text-rose-400 font-medium">{player.reception_errors}</td>
                      <td className="py-3 text-right text-emerald-400 font-bold bg-emerald-500/5 px-2 rounded">
                        {player.error_percentage}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;