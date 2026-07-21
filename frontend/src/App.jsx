import React, { useState, useEffect } from 'react';
import { fetchTeams, fetchScoutReport } from './services/api';
import { ReceptionTable } from './components/ReceptionTable';
import { AttackTable } from './components/AttackTable';
import { ServiceTable } from './components/ServiceTable';

function App() {
  const [teams, setTeams] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('reception');

  // Load initial team filters dropdown values on mount
  useEffect(() => {
    fetchTeams()
      .then((data) => setTeams(data))
      .catch((err) => console.error("Error loading filters data:", err));
  }, []);

  // Synchronize data data streams whenever parameters change
  useEffect(() => {
    if (!selectedTeamId) {
      setLeaderboard([]);
      return;
    }
    setLoading(true);
    fetchScoutReport(selectedTeamId, activeTab)
      .then((data) => {
        setLeaderboard(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [selectedTeamId, activeTab]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      {/* Page Header Banner */}
      <header className="border-b border-slate-800 pb-4 mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-emerald-400">
          Luxembourg National Volleyball League
        </h1>
        <p className="text-slate-400 mt-1">Scout & Match Analytics Tool</p>
      </header>

      {/* Main Responsive Grid Layout */}
      <main className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* 🎯 SIDEBAR FILTERS (Brought back to full operation!) */}
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

        {/* MAIN METRIC BOARD VIEWS CONTAINER */}
        <div className="md:col-span-2 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">

          {/* Dashboard View Navigation Tabs */}
          <div className="flex border-b border-slate-700 mb-6 space-x-1">
            {['reception', 'attack', 'service'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 px-4 font-medium text-sm capitalize transition-colors ${
                  activeTab === tab
                    ? 'border-b-2 border-emerald-400 text-emerald-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab === 'reception' ? 'Reception Errors' : tab === 'attack' ? 'Attack Profile' : 'Service'}
              </button>
            ))}
          </div>

          {/* Conditional Layout Switching Engines */}
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
              {/* Dynamic Presentation Component Injections */}
              {activeTab === 'reception' && <ReceptionTable data={leaderboard} />}
              {activeTab === 'attack' && <AttackTable data={leaderboard} />}
              {activeTab === 'service' && <ServiceTable data={leaderboard} />}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}

export default App;