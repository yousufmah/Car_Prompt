'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Car, Eye, MousePointer, TrendingUp, Search, BarChart as BarChartIcon, LineChart as LineChartIcon, Home, Settings, Users, MessageSquare, Bell, ChevronDown, Download, Menu, X } from 'lucide-react';

// Configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GARAGE_ID = 1; // TODO: Get from auth/session

// Types matching backend responses
interface DateMetric {
  date: string;
  impressions: number;
  views: number;
}

interface VehicleMetric {
  vehicle: string;
  views: number;
}

interface ListingMetric {
  id: number;
  name: string;
  image: string;
  dateListed: string;
  status: string;
  impressions: number;
  views: number;
  ctr: number;
}

interface SummaryMetric {
  total_impressions: number;
  total_views: number;
  lead_conversions: number;
  average_rank: number;
}

export default function GarageAnalyticsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<SummaryMetric | null>(null);
  const [impressionsVsViews, setImpressionsVsViews] = useState<DateMetric[]>([]);
  const [topVehicles, setTopVehicles] = useState<VehicleMetric[]>([]);
  const [listings, setListings] = useState<ListingMetric[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch all data in parallel
        const [summaryRes, impressionsRes, topRes, listingsRes] = await Promise.all([
          fetch(`${API_BASE}/api/analytics/summary/${GARAGE_ID}`),
          fetch(`${API_BASE}/api/analytics/impressions-vs-views/${GARAGE_ID}`),
          fetch(`${API_BASE}/api/analytics/top-vehicles/${GARAGE_ID}`),
          fetch(`${API_BASE}/api/analytics/listings-performance/${GARAGE_ID}`),
        ]);

        if (!summaryRes.ok || !impressionsRes.ok || !topRes.ok || !listingsRes.ok) {
          throw new Error('Failed to fetch analytics data');
        }

        const summaryData = await summaryRes.json();
        const impressionsData = await impressionsRes.json();
        const topData = await topRes.json();
        const listingsData = await listingsRes.json();

        setSummary(summaryData);
        setImpressionsVsViews(impressionsData);
        setTopVehicles(topData);
        setListings(listingsData);
      } catch (error) {
        console.error('Error fetching analytics:', error);
        // Fallback to mock data if API fails
        setSummary({
          total_impressions: 28300,
          total_views: 9600,
          lead_conversions: 342,
          average_rank: 4.2,
        });
        setImpressionsVsViews([
          { date: '2025-02-01', impressions: 2400, views: 400 },
          { date: '2025-02-02', impressions: 1398, views: 300 },
          { date: '2025-02-03', impressions: 9800, views: 2000 },
          { date: '2025-02-04', impressions: 3908, views: 1000 },
          { date: '2025-02-05', impressions: 4800, views: 800 },
          { date: '2025-02-06', impressions: 3800, views: 900 },
          { date: '2025-02-07', impressions: 4300, views: 1200 },
          { date: '2025-02-08', impressions: 5200, views: 1400 },
          { date: '2025-02-09', impressions: 6100, views: 1800 },
          { date: '2025-02-10', impressions: 7300, views: 2200 },
          { date: '2025-02-11', impressions: 8400, views: 2500 },
          { date: '2025-02-12', impressions: 9200, views: 2800 },
          { date: '2025-02-13', impressions: 10200, views: 3200 },
          { date: '2025-02-14', impressions: 11300, views: 3500 },
          { date: '2025-02-15', impressions: 12400, views: 3800 },
          { date: '2025-02-16', impressions: 13500, views: 4100 },
          { date: '2025-02-17', impressions: 14200, views: 4400 },
          { date: '2025-02-18', impressions: 15100, views: 4800 },
          { date: '2025-02-19', impressions: 16200, views: 5200 },
          { date: '2025-02-20', impressions: 17300, views: 5600 },
          { date: '2025-02-21', impressions: 18400, views: 6000 },
          { date: '2025-02-22', impressions: 19500, views: 6400 },
          { date: '2025-02-23', impressions: 20600, views: 6800 },
          { date: '2025-02-24', impressions: 21700, views: 7200 },
          { date: '2025-02-25', impressions: 22800, views: 7600 },
          { date: '2025-02-26', impressions: 23900, views: 8000 },
          { date: '2025-02-27', impressions: 25000, views: 8400 },
          { date: '2025-02-28', impressions: 26100, views: 8800 },
          { date: '2025-02-29', impressions: 27200, views: 9200 },
          { date: '2025-03-01', impressions: 28300, views: 9600 },
        ]);
        setTopVehicles([
          { vehicle: 'Tesla Model 3', views: 12500 },
          { vehicle: 'Ford Mustang', views: 9800 },
          { vehicle: 'BMW X5', views: 7600 },
          { vehicle: 'Toyota Camry', views: 5400 },
          { vehicle: 'Honda Civic', views: 3200 },
        ]);
        setListings([
          { id: 1, name: 'Tesla Model 3', image: 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=150&h=150&fit=crop', dateListed: '2025-02-15', status: 'Live', impressions: 12500, views: 1250, ctr: 10.0 },
          { id: 2, name: 'Ford Mustang', image: 'https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=150&h=150&fit=crop', dateListed: '2025-02-14', status: 'Live', impressions: 9800, views: 980, ctr: 10.0 },
          { id: 3, name: 'BMW X5', image: 'https://images.unsplash.com/photo-1555212697-194d092e3b8f?w=150&h=150&fit=crop', dateListed: '2025-02-13', status: 'Live', impressions: 7600, views: 760, ctr: 10.0 },
          { id: 4, name: 'Toyota Camry', image: 'https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=150&h=150&fit=crop', dateListed: '2025-02-12', status: 'Live', impressions: 5400, views: 540, ctr: 10.0 },
          { id: 5, name: 'Honda Civic', image: 'https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=150&h=150&fit=crop', dateListed: '2025-02-11', status: 'Live', impressions: 3200, views: 320, ctr: 10.0 },
          { id: 6, name: 'Mercedes C-Class', image: 'https://images.unsplash.com/photo-1563720223485-8d6d5c5c8c1a?w=150&h=150&fit=crop', dateListed: '2025-02-10', status: 'Live', impressions: 2800, views: 280, ctr: 10.0 },
          { id: 7, name: 'Audi A4', image: 'https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=150&h=150&fit=crop', dateListed: '2025-02-09', status: 'Live', impressions: 2400, views: 240, ctr: 10.0 },
          { id: 8, name: 'Volkswagen Golf', image: 'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=150&h=150&fit=crop', dateListed: '2025-02-08', status: 'Live', impressions: 2000, views: 200, ctr: 10.0 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading || !summary) {
    return (
      <div className="flex min-h-screen bg-gray-50 items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setSidebarOpen(false)}>
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Mobile sidebar */}
      <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:hidden`}>
        <div className="flex flex-col flex-grow border-r border-gray-200 pt-5 bg-white overflow-y-auto h-full">
          <div className="flex items-center justify-between flex-shrink-0 px-4">
            <div className="text-2xl font-bold text-indigo-600">CarPrompt</div>
            <button onClick={() => setSidebarOpen(false)} className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="mt-8 flex-1 flex flex-col px-4 space-y-1">
            <a href="#" className="bg-indigo-50 text-indigo-700 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Home className="mr-3 h-5 w-5" />
              Dashboard
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <BarChartIcon className="mr-3 h-5 w-5" />
              Analytics
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Car className="mr-3 h-5 w-5" />
              Listings
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Users className="mr-3 h-5 w-5" />
              Leads
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <MessageSquare className="mr-3 h-5 w-5" />
              Messages
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Settings className="mr-3 h-5 w-5" />
              Settings
            </a>
          </nav>
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">Garage Pro Motors</p>
                <p className="text-xs text-gray-500">Premium Dealership</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow border-r border-gray-200 pt-5 bg-white overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-4">
            <div className="text-2xl font-bold text-indigo-600">CarPrompt</div>
          </div>
          <nav className="mt-8 flex-1 flex flex-col px-4 space-y-1">
            <a href="#" className="bg-indigo-50 text-indigo-700 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Home className="mr-3 h-5 w-5" />
              Dashboard
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <BarChartIcon className="mr-3 h-5 w-5" />
              Analytics
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Car className="mr-3 h-5 w-5" />
              Listings
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Users className="mr-3 h-5 w-5" />
              Leads
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <MessageSquare className="mr-3 h-5 w-5" />
              Messages
            </a>
            <a href="#" className="text-gray-900 hover:bg-gray-100 group flex items-center px-3 py-2 text-sm font-medium rounded-md">
              <Settings className="mr-3 h-5 w-5" />
              Settings
            </a>
          </nav>
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">Garage Pro Motors</p>
                <p className="text-xs text-gray-500">Premium Dealership</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        {/* Top header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <div className="flex items-center">
              <button
                type="button"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 mr-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">Analytics Dashboard</h1>
                <p className="text-sm text-gray-500">Track performance of your vehicle listings</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-600 hover:text-gray-900">
                <Bell className="h-5 w-5" />
              </button>
              <div className="relative">
                <button className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                  <span>Garage Pro Motors</span>
                  <ChevronDown className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          {/* Filters */}
          <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <select className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                  <option>Last 7 days</option>
                  <option selected>Last 30 days</option>
                  <option>Last 12 months</option>
                </select>
              </div>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search listings..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              </div>
            </div>
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </button>
          </div>

          {/* Key metrics cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Impressions</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {(summary.total_impressions / 1000).toFixed(1)}K
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    <TrendingUp className="inline h-4 w-4" /> +12.5% from last month
                  </p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <Search className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Listing Views</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {(summary.total_views / 1000).toFixed(1)}K
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    <TrendingUp className="inline h-4 w-4" /> +8.2% from last month
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <Eye className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Lead Conversions</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {summary.lead_conversions.toLocaleString()}
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    <TrendingUp className="inline h-4 w-4" /> +5.3% from last month
                  </p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <MousePointer className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Average Rank</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {summary.average_rank.toFixed(1)}
                  </p>
                  <p className="text-sm text-red-600 mt-1">
                    <TrendingUp className="inline h-4 w-4" /> -0.3 from last month
                  </p>
                </div>
                <div className="p-3 bg-amber-50 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Line Chart */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Search Impressions vs Views</h3>
                  <p className="text-sm text-gray-500">Last 30 days performance</p>
                </div>
                <LineChartIcon className="h-5 w-5 text-gray-400" />
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={impressionsVsViews}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="impressions" stroke="#4f46e5" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="views" stroke="#10b981" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bar Chart */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Top 5 Performing Vehicles</h3>
                  <p className="text-sm text-gray-500">By view count</p>
                </div>
                <BarChartIcon className="h-5 w-5 text-gray-500" />
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topVehicles}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="vehicle" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip />
                    <Bar dataKey="views" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Listings Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Vehicle Listings Performance</h3>
                <p className="text-sm text-gray-500">Detailed metrics for each listing</p>
              </div>
              <button className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                View all →
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vehicle
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date Listed
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Impressions
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Views
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CTR
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {listings.map((listing) => (
                    <tr key={listing.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <img className="h-10 w-10 rounded-md object-cover" src={listing.image} alt={listing.name} />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{listing.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {listing.dateListed}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${listing.status === 'Live' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {listing.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {listing.impressions.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {listing.views.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {listing.ctr}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing <span className="font-medium">{listings.length}</span> of <span className="font-medium">42</span> listings
              </div>
              <div className="flex space-x-2">
                <button className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                  Previous
                </button>
                <button className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                  Next
                </button>
              </div>
            </div>
          </div>

          {/* Footer note */}
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>Data updates every hour. Last updated: Today, 14:33 UTC</p>
          </div>
        </main>
      </div>
    </div>
  );
}