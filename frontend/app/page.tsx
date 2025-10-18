'use client';

import { useState, useEffect } from 'react';

interface Announcement {
  id: number;
  member_id: string;
  company_name: string;
  announcement_title: string;
  description: string;
  products: string;
  location: string;
  announcement_type: string;
  announcement_date: string;
  announcement_url: string;
  scraped_date: string;
  checked: number;
  created_at: string;
}

interface Stats {
  total: number;
  checked: number;
  unchecked: number;
  today: number;
}

export default function Home() {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, checked: 0, unchecked: 0, today: 0 });
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterLocation, setFilterLocation] = useState('all');
  const [statusCheckInterval, setStatusCheckInterval] = useState<NodeJS.Timeout | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';
  const IS_PRODUCTION = process.env.NODE_ENV === 'production';

  useEffect(() => {
    fetchAnnouncements();
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchAnnouncements = async () => {
    try {
      const response = await fetch(`${API_URL}/api/announcements`);
      const data = await response.json();
      setAnnouncements(Array.isArray(data) ? data : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching announcements:', error);
      setAnnouncements([]);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const toggleCheck = async (id: number, currentChecked: number) => {
    try {
      const newChecked = currentChecked === 1 ? 0 : 1;
      await fetch(`${API_URL}/api/announcements/${id}/check`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ checked: newChecked }),
      });

      setAnnouncements(announcements.map(a =>
        a.id === id ? { ...a, checked: newChecked } : a
      ));
      fetchStats();
    } catch (error) {
      console.error('Error toggling check:', error);
    }
  };

  const startScraping = async () => {
    try {
      setScraping(true);
      await fetch(`${API_URL}/api/scrape`, { method: 'POST' });

      const checkStatus = setInterval(async () => {
        const response = await fetch(`${API_URL}/api/scrape/status`);
        const status = await response.json();

        if (!status.running) {
          clearInterval(checkStatus);
          setScraping(false);
          // Auto-reload data when scraping completes
          await fetchAnnouncements();
          await fetchStats();
          alert(status.message + '\n\nPage will refresh to show new results!');
          window.location.reload();
        }
      }, 2000);

      setStatusCheckInterval(checkStatus);
    } catch (error) {
      console.error('Error starting scrape:', error);
      setScraping(false);
    }
  };

  const stopScraping = () => {
    if (statusCheckInterval) {
      clearInterval(statusCheckInterval);
      setStatusCheckInterval(null);
    }
    setScraping(false);
    // Reload data to show what was scraped so far
    fetchAnnouncements();
    fetchStats();
    alert('Scraping stopped! Showing results scraped so far.');
  };

  const filteredAnnouncements = Array.isArray(announcements)
    ? announcements.filter(a => {
      // Search filter
      const matchesSearch = searchTerm === '' ||
        a.announcement_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.products.toLowerCase().includes(searchTerm.toLowerCase());

      // Type filter
      const matchesType = filterType === 'all' || a.announcement_type === filterType;

      // Location filter
      const matchesLocation = filterLocation === 'all' || a.location === filterLocation;

      return matchesSearch && matchesType && matchesLocation;
    })
    : [];

  // Get unique types and locations for filters
  const uniqueTypes = Array.from(new Set(announcements.map(a => a.announcement_type))).filter(Boolean);
  const uniqueLocations = Array.from(new Set(announcements.map(a => a.location))).filter(Boolean);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            EspaceAgro Scraper Dashboard
          </h1>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
              <div className="text-sm text-gray-600">Total Announcements</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.checked}</div>
              <div className="text-sm text-gray-600">Checked</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{stats.unchecked}</div>
              <div className="text-sm text-gray-600">Unchecked</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{stats.today}</div>
              <div className="text-sm text-gray-600">Added Today</div>
            </div>
          </div>

          {/* Controls */}
          <div className="space-y-4 mb-6">
            {/* Scraping Buttons */}
            {!IS_PRODUCTION && (
              <div className="flex gap-4">
                <button
                  onClick={startScraping}
                  disabled={scraping}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {scraping ? '🔄 Scraping...' : '▶️ Start Scraping'}
                </button>
                {scraping && (
                  <button
                    onClick={stopScraping}
                    className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
                  >
                    ⏹️ Stop Scraping
                  </button>
                )}
                <button
                  onClick={() => { fetchAnnouncements(); fetchStats(); }}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                >
                  🔄 Refresh Data
                </button>
              </div>
            )}

            {/* Search and Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="text"
                placeholder="🔍 Search announcements..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />

              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                {uniqueTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>

              <select
                value={filterLocation}
                onChange={(e) => setFilterLocation(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Locations</option>
                {uniqueLocations.map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>

            {/* Active Filters Display */}
            {(searchTerm || filterType !== 'all' || filterLocation !== 'all') && (
              <div className="flex gap-2 items-center text-sm">
                <span className="text-gray-600">Active filters:</span>
                {searchTerm && (
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                    Search: &ldquo;{searchTerm}&rdquo;
                  </span>
                )}
                {filterType !== 'all' && (
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                    Type: {filterType}
                  </span>
                )}
                {filterLocation !== 'all' && (
                  <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
                    Location: {filterLocation}
                  </span>
                )}
                <button
                  onClick={() => { setSearchTerm(''); setFilterType('all'); setFilterLocation('all'); }}
                  className="text-red-600 hover:text-red-800 ml-2"
                >
                  ✕ Clear all
                </button>
              </div>
            )}

            {/* Results Count */}
            <div className="text-sm text-gray-600">
              Showing {filteredAnnouncements.length} of {announcements.length} announcements
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">✓</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Title</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Location</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Products</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Link</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredAnnouncements.map((announcement) => (
                    <tr
                      key={announcement.id}
                      className={`hover:bg-gray-50 ${announcement.checked ? 'bg-green-50' : ''}`}
                    >
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={announcement.checked === 1}
                          onChange={() => toggleCheck(announcement.id, announcement.checked)}
                          className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500 cursor-pointer"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm font-medium text-gray-900">
                          {announcement.announcement_title}
                        </div>
                        <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                          {announcement.description}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {announcement.announcement_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">{announcement.location}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{announcement.products}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{announcement.announcement_date}</td>
                      <td className="px-4 py-3">
                        <a
                          href={announcement.announcement_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          View →
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
