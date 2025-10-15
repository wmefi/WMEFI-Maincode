import React, { useState, useEffect } from 'react';
import { Menu, X, BarChart3, Users, ClipboardList, Calendar, Settings, HelpCircle, Search, Filter, Download, Bell, User, TrendingUp, TrendingDown, Clock, CheckCircle, AlertCircle, MapPin, Phone, Mail, Eye, CreditCard as Edit, Trash2, Plus, RefreshCw, Activity, Target, Award, Globe, Calendar as CalendarIcon, FileText, Database, Shield, Zap, Star, MessageCircle, BookOpen, Video, ExternalLink, ChevronRight, ChevronDown, PieChart, BarChart, LineChart } from 'lucide-react';

interface Researcher {
  id: string;
  name: string;
  mobile: string;
  email: string;
  unit: string;
  specialty: string;
  zsm: string;
  bdm: string;
  mode: 'CP' | 'GC';
  status: 'completed' | 'pending' | 'in-progress' | 'not-started';
  completionDate?: string;
  location: string;
  experience: number;
  rating: number;
  lastActivity: string;
  surveyProgress: number;
  department: string;
  joinDate: string;
}

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMode, setFilterMode] = useState<'all' | 'CP' | 'GC'>('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'pending' | 'in-progress' | 'not-started'>('all');
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [researchers, setResearchers] = useState<Researcher[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [dashboardStats, setDashboardStats] = useState({
    totalResearchers: 0,
    completedSurveys: 0,
    inProgressSurveys: 0,
    pendingSurveys: 0,
    notStartedSurveys: 0,
    cpResearchers: 0,
    gcResearchers: 0,
    completionRate: 0,
  });

  // Helper functions to avoid NaN when totals are zero
  const percent = (value: number, total: number) => (total > 0 ? Math.round((value / total) * 100) : 0);
  const percentWidth = (value: number, total: number) => `${total > 0 ? (value / total) * 100 : 0}%`;

  // Fetch researchers data from Django API
  const fetchResearchers = async () => {
    try {
      const apiUrl = '/api/researchers/';
      
      const response = await fetch(apiUrl);
      const data = await response.json();
      if (data.success) {
        setResearchers(data.researchers);
      } else {
        console.error('API returned success: false');
      }
    } catch (error) {
      console.error('Error fetching researchers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch dashboard stats from Django API
  const fetchDashboardStats = async () => {
    try {
      const apiUrl = '/api/dashboard-stats/';
      
      const response = await fetch(apiUrl);
      const data = await response.json();
      if (data.success) {
        setDashboardStats(data.stats);
      } else {
        console.error('Dashboard stats API returned success: false');
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };
  
  useEffect(() => {
    fetchResearchers();
    fetchDashboardStats();
  }, []);

  // Refresh data when tab changes
  useEffect(() => {
    fetchResearchers();
    fetchDashboardStats();
  }, [currentPage]);

  // Enhanced mock data with more researchers and details (FALLBACK - will be replaced by API)
  const mockResearchers: Researcher[] = [
    {
      id: '1',
      name: 'Dr. Sarah Johnson',
      mobile: '+1-555-0101',
      email: 'sarah.johnson@hospital.com',
      unit: 'Cardiology',
      specialty: 'Interventional Cardiology',
      zsm: 'Michael Chen',
      bdm: 'Lisa Rodriguez',
      mode: 'CP',
      status: 'completed',
      completionDate: '2024-01-15',
      location: 'New York, NY',
      experience: 12,
      rating: 4.8,
      lastActivity: '2 hours ago',
      surveyProgress: 100,
      department: 'Cardiovascular Medicine',
      joinDate: '2023-03-15'
    },
    {
      id: '2',
      name: 'Dr. Robert Kim',
      mobile: '+1-555-0102',
      email: 'robert.kim@clinic.com',
      unit: 'Neurology',
      specialty: 'Neurological Surgery',
      zsm: 'Jennifer Walsh',
      bdm: 'David Park',
      mode: 'GC',
      status: 'in-progress',
      location: 'Los Angeles, CA',
      experience: 8,
      rating: 4.6,
      lastActivity: '1 day ago',
      surveyProgress: 65,
      department: 'Neurosciences',
      joinDate: '2023-05-20'
    },
    {
      id: '3',
      name: 'Dr. Emily Davis',
      mobile: '+1-555-0103',
      email: 'emily.davis@medical.com',
      unit: 'Oncology',
      specialty: 'Medical Oncology',
      zsm: 'Michael Chen',
      bdm: 'Sarah Thompson',
      mode: 'CP',
      status: 'pending',
      location: 'Chicago, IL',
      experience: 15,
      rating: 4.9,
      lastActivity: '3 days ago',
      surveyProgress: 25,
      department: 'Cancer Center',
      joinDate: '2023-01-10'
    },
    {
      id: '4',
      name: 'Dr. James Wilson',
      mobile: '+1-555-0104',
      email: 'james.wilson@health.com',
      unit: 'Orthopedics',
      specialty: 'Spine Surgery',
      zsm: 'Jennifer Walsh',
      bdm: 'Mark Johnson',
      mode: 'GC',
      status: 'completed',
      completionDate: '2024-01-12',
      location: 'Houston, TX',
      experience: 20,
      rating: 4.7,
      lastActivity: '5 hours ago',
      surveyProgress: 100,
      department: 'Orthopedic Surgery',
      joinDate: '2022-11-05'
    },
    {
      id: '5',
      name: 'Dr. Maria Garcia',
      mobile: '+1-555-0105',
      email: 'maria.garcia@hospital.com',
      unit: 'Pediatrics',
      specialty: 'Pediatric Cardiology',
      zsm: 'Michael Chen',
      bdm: 'Lisa Rodriguez',
      mode: 'CP',
      status: 'not-started',
      location: 'Miami, FL',
      experience: 6,
      rating: 4.5,
      lastActivity: '1 week ago',
      surveyProgress: 0,
      department: 'Children\'s Hospital',
      joinDate: '2023-08-12'
    },
    {
      id: '6',
      name: 'Dr. Thomas Anderson',
      mobile: '+1-555-0106',
      email: 'thomas.anderson@clinic.com',
      unit: 'Radiology',
      specialty: 'Interventional Radiology',
      zsm: 'Jennifer Walsh',
      bdm: 'David Park',
      mode: 'GC',
      status: 'in-progress',
      location: 'Seattle, WA',
      experience: 10,
      rating: 4.4,
      lastActivity: '6 hours ago',
      surveyProgress: 80,
      department: 'Diagnostic Imaging',
      joinDate: '2023-04-18'
    },
    {
      id: '7',
      name: 'Dr. Jennifer Lee',
      mobile: '+1-555-0107',
      email: 'jennifer.lee@medical.com',
      unit: 'Dermatology',
      specialty: 'Dermatopathology',
      zsm: 'Michael Chen',
      bdm: 'Sarah Thompson',
      mode: 'CP',
      status: 'completed',
      completionDate: '2024-01-18',
      location: 'Boston, MA',
      experience: 14,
      rating: 4.8,
      lastActivity: '1 hour ago',
      surveyProgress: 100,
      department: 'Dermatology',
      joinDate: '2022-12-03'
    },
    {
      id: '8',
      name: 'Dr. Michael Brown',
      mobile: '+1-555-0108',
      email: 'michael.brown@health.com',
      unit: 'Gastroenterology',
      specialty: 'Hepatology',
      zsm: 'Jennifer Walsh',
      bdm: 'Mark Johnson',
      mode: 'GC',
      status: 'pending',
      location: 'Phoenix, AZ',
      experience: 18,
      rating: 4.6,
      lastActivity: '2 days ago',
      surveyProgress: 15,
      department: 'Digestive Health',
      joinDate: '2023-02-28'
    },
    {
      id: '9',
      name: 'Dr. Lisa Wang',
      mobile: '+1-555-0109',
      email: 'lisa.wang@hospital.com',
      unit: 'Psychiatry',
      specialty: 'Child Psychiatry',
      zsm: 'Michael Chen',
      bdm: 'Lisa Rodriguez',
      mode: 'CP',
      status: 'in-progress',
      location: 'San Francisco, CA',
      experience: 9,
      rating: 4.7,
      lastActivity: '4 hours ago',
      surveyProgress: 45,
      department: 'Mental Health',
      joinDate: '2023-06-10'
    },
    {
      id: '10',
      name: 'Dr. David Miller',
      mobile: '+1-555-0110',
      email: 'david.miller@clinic.com',
      unit: 'Urology',
      specialty: 'Urologic Oncology',
      zsm: 'Jennifer Walsh',
      bdm: 'David Park',
      mode: 'GC',
      status: 'completed',
      completionDate: '2024-01-20',
      location: 'Denver, CO',
      experience: 16,
      rating: 4.9,
      lastActivity: '30 minutes ago',
      surveyProgress: 100,
      department: 'Urology',
      joinDate: '2022-09-15'
    },
    {
      id: '11',
      name: 'Dr. Amanda Taylor',
      mobile: '+1-555-0111',
      email: 'amanda.taylor@medical.com',
      unit: 'Endocrinology',
      specialty: 'Diabetes & Metabolism',
      zsm: 'Michael Chen',
      bdm: 'Sarah Thompson',
      mode: 'CP',
      status: 'not-started',
      location: 'Atlanta, GA',
      experience: 7,
      rating: 4.3,
      lastActivity: '5 days ago',
      surveyProgress: 0,
      department: 'Endocrine Center',
      joinDate: '2023-07-22'
    },
    {
      id: '12',
      name: 'Dr. Christopher Davis',
      mobile: '+1-555-0112',
      email: 'christopher.davis@health.com',
      unit: 'Pulmonology',
      specialty: 'Critical Care Medicine',
      zsm: 'Jennifer Walsh',
      bdm: 'Mark Johnson',
      mode: 'GC',
      status: 'in-progress',
      location: 'Portland, OR',
      experience: 11,
      rating: 4.5,
      lastActivity: '8 hours ago',
      surveyProgress: 70,
      department: 'Pulmonary Medicine',
      joinDate: '2023-03-08'
    }
  ];

  const filteredResearchers = researchers.filter(researcher => {
    const searchLower = searchTerm.toLowerCase();
    const matchesSearch = researcher.name.toLowerCase().includes(searchLower) ||
                         researcher.unit.toLowerCase().includes(searchLower) ||
                         researcher.specialty.toLowerCase().includes(searchLower) ||
                         researcher.zsm.toLowerCase().includes(searchLower) ||
                         researcher.bdm.toLowerCase().includes(searchLower) ||
                         researcher.location.toLowerCase().includes(searchLower) ||
                         researcher.mobile.includes(searchTerm);
    const matchesMode = filterMode === 'all' || researcher.mode === filterMode;
    const matchesStatus = filterStatus === 'all' || researcher.status === filterStatus;
    return matchesSearch && matchesMode && matchesStatus;
  });

  // Use API stats if available, otherwise calculate from researchers data
  const totalResearchers = dashboardStats.totalResearchers || researchers.length;
  const completedSurveys = dashboardStats.completedSurveys || researchers.filter(r => r.status === 'completed').length;
  const pendingSurveys = dashboardStats.pendingSurveys || researchers.filter(r => r.status === 'pending').length;
  const inProgressSurveys = dashboardStats.inProgressSurveys || researchers.filter(r => r.status === 'in-progress').length;
  const notStartedSurveys = dashboardStats.notStartedSurveys || researchers.filter(r => r.status === 'not-started').length;
  const cpResearchers = dashboardStats.cpResearchers || researchers.filter(r => r.mode === 'CP').length;
  const gcResearchers = dashboardStats.gcResearchers || researchers.filter(r => r.mode === 'GC').length;
  const completionRate = dashboardStats.completionRate || (totalResearchers > 0 ? Math.round((completedSurveys / totalResearchers) * 100) : 0);

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in-progress': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'not-started': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress === 100) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress > 0) return 'bg-yellow-500';
    return 'bg-gray-300';
  };

  const exportToCSV = () => {
    const headers = ['Name', 'Mobile', 'Email', 'Unit', 'Specialty', 'ZSM', 'BDM', 'Mode', 'Status', 'Progress', 'Location'];
    const csvContent = [
      headers.join(','),
      ...filteredResearchers.map(r => [
        r.name, r.mobile, r.email, r.unit, r.specialty, r.zsm, r.bdm, r.mode, r.status, `${r.surveyProgress}%`, r.location
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'researchers_data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'researchers', label: 'Researchers', icon: Users },
    { id: 'survey-status', label: 'Survey Status', icon: ClipboardList },
    { id: 'schedule', label: 'Schedule', icon: Calendar },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'help', label: 'Help & Support', icon: HelpCircle },
  ];

  const renderDashboard = () => (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">WMEFI Access Dashboard</h1>
            <p className="text-pink-100 text-lg">Real-time survey monitoring and researcher management</p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2 mb-2">
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">Last updated: {lastUpdated.toLocaleTimeString()}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-green-300" />
              <span className="text-sm">System Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Researchers</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{totalResearchers}</p>
              <div className="flex items-center mt-2">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-500 text-sm font-medium">+12% this month</span>
              </div>
            </div>
            <div className="bg-gradient-to-br from-pink-500 to-pink-600 p-3 rounded-xl">
              <Users className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Completion Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{completionRate}%</p>
              <div className="flex items-center mt-2">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-500 text-sm font-medium">+8% this week</span>
              </div>
            </div>
            <div className="bg-gradient-to-br from-teal-500 to-teal-600 p-3 rounded-xl">
              <Target className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Completed Surveys</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{completedSurveys}</p>
              <div className="flex items-center mt-2">
                <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-500 text-sm font-medium">{completedSurveys} of {totalResearchers}</span>
              </div>
            </div>
            <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 p-3 rounded-xl">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Pending Surveys</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{pendingSurveys + inProgressSurveys}</p>
              <div className="flex items-center mt-2">
                <Clock className="w-4 h-4 text-yellow-500 mr-1" />
                <span className="text-yellow-500 text-sm font-medium">Needs attention</span>
              </div>
            </div>
            <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 p-3 rounded-xl">
              <Clock className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Mode Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Mode Distribution</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-pink-500 rounded-full mr-3"></div>
                <span className="font-medium text-gray-700">CP (Clinical Practice)</span>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-gray-900">{cpResearchers}</span>
                <span className="text-gray-500 text-sm ml-1">({percent(cpResearchers, totalResearchers)}%)</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div className="bg-gradient-to-r from-pink-500 to-pink-600 h-3 rounded-full transition-all duration-500" 
                   style={{width: percentWidth(cpResearchers, totalResearchers)}}></div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-teal-500 rounded-full mr-3"></div>
                <span className="font-medium text-gray-700">GC (General Care)</span>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-gray-900">{gcResearchers}</span>
                <span className="text-gray-500 text-sm ml-1">({percent(gcResearchers, totalResearchers)}%)</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div className="bg-gradient-to-r from-teal-500 to-teal-600 h-3 rounded-full transition-all duration-500" 
                   style={{width: percentWidth(gcResearchers, totalResearchers)}}></div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Survey Status Overview</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                <span className="font-medium text-green-800">Completed</span>
              </div>
              <span className="text-2xl font-bold text-green-600">{completedSurveys}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-blue-600 mr-3" />
                <span className="font-medium text-blue-800">In Progress</span>
              </div>
              <span className="text-2xl font-bold text-blue-600">{inProgressSurveys}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-yellow-600 mr-3" />
                <span className="font-medium text-yellow-800">Pending</span>
              </div>
              <span className="text-2xl font-bold text-yellow-600">{pendingSurveys}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-gray-600 mr-3" />
                <span className="font-medium text-gray-800">Not Started</span>
              </div>
              <span className="text-2xl font-bold text-gray-600">{notStartedSurveys}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-2xl p-12 shadow-lg border border-gray-100 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      )}

      {/* Search and Filters */}
      {!isLoading && (
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <h3 className="text-xl font-bold text-gray-900">Researcher Details</h3>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search by name, specialty, manager, territory, mobile..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent w-96"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value as any)}
            >
              <option value="all">All Modes</option>
              <option value="CP">CP Only</option>
              <option value="GC">GC Only</option>
            </select>
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as any)}
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="in-progress">In Progress</option>
              <option value="pending">Pending</option>
              <option value="not-started">Not Started</option>
            </select>
            <button
              onClick={exportToCSV}
              className="flex items-center px-4 py-2 bg-gradient-to-r from-pink-600 to-teal-600 text-white rounded-lg hover:from-pink-700 hover:to-teal-700 transition-all duration-200"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Researchers Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Researcher</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Contact</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Unit & Specialty</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Assignment</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Mode</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Progress</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredResearchers.map((researcher) => (
                <tr key={researcher.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200">
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-teal-500 rounded-full flex items-center justify-center text-white font-semibold mr-3">
                        {researcher.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{researcher.name}</div>
                        <div className="text-sm text-gray-500 flex items-center">
                          <MapPin className="w-3 h-3 mr-1" />
                          {researcher.location}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="space-y-1">
                      <div className="flex items-center text-sm text-gray-600">
                        <Phone className="w-3 h-3 mr-2" />
                        {researcher.mobile}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Mail className="w-3 h-3 mr-2" />
                        {researcher.email}
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div>
                      <div className="font-medium text-gray-900">{researcher.unit}</div>
                      <div className="text-sm text-gray-500">{researcher.specialty}</div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div>
                      <div className="text-sm text-gray-600">ZSM: {researcher.zsm}</div>
                      <div className="text-sm text-gray-600">BDM: {researcher.bdm}</div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      researcher.mode === 'CP' 
                        ? 'bg-pink-100 text-pink-800' 
                        : 'bg-teal-100 text-teal-800'
                    }`}>
                      {researcher.mode}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(researcher.status)}`}>
                      {researcher.status.replace('-', ' ')}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(researcher.surveyProgress)}`}
                          style={{width: `${researcher.surveyProgress}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-600 min-w-[40px]">{researcher.surveyProgress}%</span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center space-x-2">
                      <button className="p-1 text-gray-400 hover:text-blue-600 transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-green-600 transition-colors">
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      )}
    </div>
  );

  const handleRefresh = () => {
    setIsLoading(true);
    fetchResearchers();
    fetchDashboardStats();
    setLastUpdated(new Date());
  };

  const renderAnalytics = () => (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Advanced Analytics</h1>
            <p className="text-pink-100 text-lg">Comprehensive insights and performance metrics</p>
          </div>
          <button 
            onClick={handleRefresh}
            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-xl text-white font-medium transition-all duration-200 flex items-center"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Response Rate</h3>
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">{completionRate}%</div>
          <div className="text-sm text-green-600 font-medium">{completedSurveys} of {totalResearchers} completed</div>
          <div className="mt-4 h-32 bg-gradient-to-r from-green-100 to-green-200 rounded-lg flex items-end justify-center">
            <BarChart className="w-16 h-16 text-green-600 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Active Surveys</h3>
            <Clock className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">{inProgressSurveys}</div>
          <div className="text-sm text-blue-600 font-medium">In progress right now</div>
          <div className="mt-4 h-32 bg-gradient-to-r from-blue-100 to-blue-200 rounded-lg flex items-end justify-center">
            <LineChart className="w-16 h-16 text-blue-600 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Average Progress</h3>
            <Award className="w-5 h-5 text-yellow-500" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {researchers.length > 0 ? Math.round(researchers.reduce((sum, r) => sum + r.surveyProgress, 0) / researchers.length) : 0}%
          </div>
          <div className="text-sm text-yellow-600 font-medium">Overall completion</div>
          <div className="mt-4 h-32 bg-gradient-to-r from-yellow-100 to-yellow-200 rounded-lg flex items-end justify-center">
            <PieChart className="w-16 h-16 text-yellow-600 opacity-50" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Performance by Department</h3>
          <div className="space-y-4">
            {(() => {
              // Group researchers by department/specialty
              const deptStats = researchers.reduce((acc, r) => {
                const dept = r.unit || r.specialty || 'General';
                if (!acc[dept]) acc[dept] = { total: 0, completed: 0 };
                acc[dept].total++;
                if (r.status === 'completed') acc[dept].completed++;
                return acc;
              }, {} as Record<string, { total: number; completed: number }>);

              // Convert to array and sort by total count
              return Object.entries(deptStats)
                .sort((a, b) => b[1].total - a[1].total)
                .slice(0, 5)
                .map(([dept, stats]) => {
                  const percentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
                  return (
                    <div key={dept} className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-gray-700">{dept}</span>
                        <div className="text-xs text-gray-500">{stats.completed}/{stats.total} completed</div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-pink-500 to-teal-500 h-2 rounded-full transition-all duration-500"
                            style={{width: `${percentage}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-600 w-12">{percentage}%</span>
                      </div>
                    </div>
                  );
                });
            })()}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Geographic Distribution</h3>
          <div className="space-y-4">
            {(() => {
              // Group researchers by location
              const locationStats = researchers.reduce((acc, r) => {
                const loc = r.location || 'Unknown';
                if (!acc[loc]) acc[loc] = 0;
                acc[loc]++;
                return acc;
              }, {} as Record<string, number>);

              const total = researchers.length;
              
              // Convert to array and sort by count
              return Object.entries(locationStats)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([location, count]) => {
                  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                  return (
                    <div key={location} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                        <span className="font-medium text-gray-700">{location}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-sm text-gray-600">{count} researcher{count !== 1 ? 's' : ''}</span>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-cyan-500 to-teal-500 h-2 rounded-full transition-all duration-500"
                            style={{width: `${percentage}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-600 w-8">{percentage}%</span>
                      </div>
                    </div>
                  );
                });
            })()}
          </div>
        </div>
      </div>
    </div>
  );

  const renderResearchers = () => (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Researcher Management</h1>
            <p className="text-pink-100 text-lg">Comprehensive researcher profiles and management • {totalResearchers} Total</p>
          </div>
          <div className="flex items-center space-x-3">
            <button 
              onClick={handleRefresh}
              className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-xl text-white font-medium transition-all duration-200 flex items-center"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-xl text-white font-medium transition-all duration-200 flex items-center">
              <Plus className="w-5 h-5 mr-2" />
              Add Researcher
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {researchers.map((researcher) => (
          <div key={researcher.id} className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-teal-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                {researcher.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className={`w-4 h-4 ${i < Math.floor(researcher.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                ))}
                <span className="text-sm text-gray-600 ml-1">{researcher.rating}</span>
              </div>
            </div>
            
            <h3 className="text-xl font-bold text-gray-900 mb-2">{researcher.name}</h3>
            <p className="text-gray-600 mb-4">{researcher.specialty}</p>
            
            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm text-gray-600">
                <MapPin className="w-4 h-4 mr-2" />
                {researcher.location}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Phone className="w-4 h-4 mr-2" />
                {researcher.mobile}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Mail className="w-4 h-4 mr-2" />
                {researcher.email}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Award className="w-4 h-4 mr-2" />
                {researcher.experience} years experience
              </div>
            </div>

            <div className="flex items-center justify-between mb-4">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                researcher.mode === 'CP' ? 'bg-pink-100 text-pink-800' : 'bg-teal-100 text-teal-800'
              }`}>
                {researcher.mode}
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(researcher.status)}`}>
                {researcher.status.replace('-', ' ')}
              </span>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Survey Progress</span>
                <span className="text-sm font-medium text-gray-600">{researcher.surveyProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(researcher.surveyProgress)}`}
                  style={{width: `${researcher.surveyProgress}%`}}
                ></div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Last active: {researcher.lastActivity}</span>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200">
                  <Eye className="w-4 h-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-pink-600 hover:bg-pink-50 rounded-lg transition-all duration-200">
                  <MessageCircle className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSurveyStatus = () => (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Survey Status Tracking</h1>
            <p className="text-pink-100 text-lg">Real-time survey completion monitoring • {completedSurveys}/{totalResearchers} Completed</p>
          </div>
          <button 
            onClick={handleRefresh}
            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-xl text-white font-medium transition-all duration-200 flex items-center"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Survey Activities</h3>
          <div className="space-y-4">
            {[
              { name: 'Dr. Sarah Johnson', action: 'Completed survey', time: '2 hours ago', status: 'completed' },
              { name: 'Dr. David Miller', action: 'Completed survey', time: '30 minutes ago', status: 'completed' },
              { name: 'Dr. Lisa Wang', action: 'Started survey', time: '4 hours ago', status: 'in-progress' },
              { name: 'Dr. Thomas Anderson', action: 'Updated progress', time: '6 hours ago', status: 'in-progress' },
              { name: 'Dr. Jennifer Lee', action: 'Completed survey', time: '1 hour ago', status: 'completed' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-teal-500 rounded-full flex items-center justify-center text-white font-semibold text-sm mr-3">
                    {activity.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{activity.name}</div>
                    <div className="text-sm text-gray-600">{activity.action}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">{activity.time}</div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                    {activity.status.replace('-', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Survey Completion Timeline</h3>
          <div className="space-y-6">
            {researchers.filter(r => r.status === 'completed').slice(0, 5).map((researcher, index) => (
              <div key={researcher.id} className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-4">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
                <div className="flex-grow">
                  <div className="font-medium text-gray-900">{researcher.name}</div>
                  <div className="text-sm text-gray-600">{researcher.unit} • {researcher.specialty}</div>
                  <div className="text-xs text-gray-500">Completed on {researcher.completionDate}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-green-600">100%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Detailed Survey Progress</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Researcher</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Department</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Progress</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Last Update</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {researchers.map((researcher) => (
                <tr key={researcher.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200">
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-teal-500 rounded-full flex items-center justify-center text-white font-semibold text-sm mr-3">
                        {researcher.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{researcher.name}</div>
                        <div className="text-sm text-gray-500">{researcher.mode}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="font-medium text-gray-900">{researcher.unit}</div>
                    <div className="text-sm text-gray-500">{researcher.specialty}</div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(researcher.surveyProgress)}`}
                          style={{width: `${researcher.surveyProgress}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-600">{researcher.surveyProgress}%</span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(researcher.status)}`}>
                      {researcher.status.replace('-', ' ')}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm text-gray-600">{researcher.lastActivity}</span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center space-x-2">
                      <button className="p-1 text-gray-400 hover:text-blue-600 transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-green-600 transition-colors">
                        <MessageCircle className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderSchedule = () => (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Survey Schedule</h1>
            <p className="text-pink-100 text-lg">Manage survey timelines • {inProgressSurveys} Active • {pendingSurveys} Pending</p>
          </div>
          <div className="flex items-center space-x-3">
            <button 
              onClick={handleRefresh}
              className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-xl text-white font-medium transition-all duration-200 flex items-center"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-xl text-white font-medium transition-all duration-200 flex items-center">
              <Plus className="w-5 h-5 mr-2" />
              Schedule Survey
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Today's Schedule</h3>
          <div className="space-y-3">
            {[
              { time: '09:00 AM', researcher: 'Dr. Sarah Johnson', type: 'Follow-up Call' },
              { time: '11:30 AM', researcher: 'Dr. Robert Kim', type: 'Survey Review' },
              { time: '02:00 PM', researcher: 'Dr. Emily Davis', type: 'Initial Contact' },
              { time: '04:30 PM', researcher: 'Dr. James Wilson', type: 'Progress Check' }
            ].map((appointment, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">{appointment.time}</div>
                  <div className="text-sm text-gray-600">{appointment.researcher}</div>
                  <div className="text-xs text-gray-500">{appointment.type}</div>
                </div>
                <CalendarIcon className="w-5 h-5 text-gray-400" />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Upcoming Deadlines</h3>
          <div className="space-y-3">
            {[
              { date: 'Jan 25', researcher: 'Dr. Maria Garcia', task: 'Survey Completion', priority: 'high' },
              { date: 'Jan 27', researcher: 'Dr. Thomas Anderson', task: 'Progress Review', priority: 'medium' },
              { date: 'Jan 30', researcher: 'Dr. Amanda Taylor', task: 'Initial Survey', priority: 'low' },
              { date: 'Feb 02', researcher: 'Dr. Christopher Davis', task: 'Follow-up', priority: 'medium' }
            ].map((deadline, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">{deadline.date}</div>
                  <div className="text-sm text-gray-600">{deadline.researcher}</div>
                  <div className="text-xs text-gray-500">{deadline.task}</div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  deadline.priority === 'high' ? 'bg-red-100 text-red-800' :
                  deadline.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {deadline.priority}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Calendar Overview</h3>
          <div className="grid grid-cols-7 gap-1 mb-4">
            {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day) => (
              <div key={day} className="text-center text-xs font-medium text-gray-500 p-2">{day}</div>
            ))}
            {Array.from({length: 31}, (_, i) => i + 1).map((day) => (
              <div key={day} className={`text-center text-sm p-2 rounded cursor-pointer transition-colors ${
                day === 22 ? 'bg-pink-500 text-white' :
                [15, 18, 25, 27].includes(day) ? 'bg-teal-100 text-teal-800' :
                'hover:bg-gray-100'
              }`}>
                {day}
              </div>
            ))}
          </div>
          <div className="text-xs text-gray-500">
            <div className="flex items-center mb-1">
              <div className="w-3 h-3 bg-pink-500 rounded-full mr-2"></div>
              Today
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-teal-100 rounded-full mr-2"></div>
              Scheduled Events
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Survey Timeline</h3>
        <div className="space-y-6">
          {researchers.slice(0, 6).map((researcher, index) => (
            <div key={researcher.id} className="flex items-center">
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-pink-500 to-teal-500 rounded-full flex items-center justify-center text-white font-semibold mr-4">
                {researcher.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="flex-grow">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-gray-900">{researcher.name}</div>
                  <div className="text-sm text-gray-500">
                    {researcher.status === 'completed' ? `Completed ${researcher.completionDate}` : 
                     researcher.status === 'in-progress' ? 'In Progress' :
                     researcher.status === 'pending' ? 'Pending Start' : 'Not Started'}
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(researcher.surveyProgress)}`}
                    style={{width: `${researcher.surveyProgress}%`}}
                  ></div>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm text-gray-600">{researcher.unit}</span>
                  <span className="text-sm font-medium text-gray-600">{researcher.surveyProgress}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">Settings & Configuration</h1>
        <p className="text-pink-100 text-lg">Manage system preferences and data export options</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">System Preferences</h3>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Real-time Updates</div>
                <div className="text-sm text-gray-600">Automatically refresh data every 30 seconds</div>
              </div>
              <div className="relative">
                <input type="checkbox" className="sr-only" defaultChecked />
                <div className="w-12 h-6 bg-pink-500 rounded-full shadow-inner"></div>
                <div className="absolute w-4 h-4 bg-white rounded-full shadow top-1 right-1 transition"></div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Email Notifications</div>
                <div className="text-sm text-gray-600">Receive alerts for survey completions</div>
              </div>
              <div className="relative">
                <input type="checkbox" className="sr-only" defaultChecked />
                <div className="w-12 h-6 bg-pink-500 rounded-full shadow-inner"></div>
                <div className="absolute w-4 h-4 bg-white rounded-full shadow top-1 right-1 transition"></div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Dark Mode</div>
                <div className="text-sm text-gray-600">Switch to dark theme</div>
              </div>
              <button 
                onClick={() => setDarkMode(!darkMode)}
                className="relative w-12 h-6 rounded-full shadow-inner transition-colors duration-200 focus:outline-none"
                style={{ backgroundColor: darkMode ? '#ec4899' : '#d1d5db' }}
              >
                <div 
                  className="absolute w-4 h-4 bg-white rounded-full shadow top-1 transition-transform duration-200"
                  style={{ transform: darkMode ? 'translateX(24px)' : 'translateX(4px)' }}
                ></div>
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Data Export</h3>
          <div className="space-y-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-900">Complete Dataset</div>
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <div className="text-sm text-gray-600 mb-3">Export all researcher data and survey responses</div>
              <button className="w-full bg-gradient-to-r from-pink-600 to-teal-600 text-white py-2 px-4 rounded-lg hover:from-pink-700 hover:to-teal-700 transition-all duration-200">
                Export as CSV
              </button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-900">Analytics Report</div>
                <BarChart3 className="w-5 h-5 text-gray-400" />
              </div>
              <div className="text-sm text-gray-600 mb-3">Export performance metrics and analytics</div>
              <button className="w-full bg-gradient-to-r from-pink-600 to-teal-600 text-white py-2 px-4 rounded-lg hover:from-pink-700 hover:to-teal-700 transition-all duration-200">
                Export as PDF
              </button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-900">Custom Export</div>
                <Database className="w-5 h-5 text-gray-400" />
              </div>
              <div className="text-sm text-gray-600 mb-3">Select specific fields and date ranges</div>
              <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-all duration-200">
                Configure Export
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings and API Configuration removed - dummy data */}
      {/*
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Security Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Shield className="w-5 h-5 text-green-600 mr-3" />
                <div>
                  <div className="font-medium text-gray-900">Two-Factor Authentication</div>
                  <div className="text-sm text-gray-600">Enabled</div>
                </div>
              </div>
              <button className="text-pink-600 hover:text-pink-700 font-medium">Configure</button>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Globe className="w-5 h-5 text-blue-600 mr-3" />
                <div>
                  <div className="font-medium text-gray-900">IP Restrictions</div>
                  <div className="text-sm text-gray-600">3 allowed IPs</div>
                </div>
              </div>
              <button className="text-pink-600 hover:text-pink-700 font-medium">Manage</button>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-yellow-600 mr-3" />
                <div>
                  <div className="font-medium text-gray-900">Session Timeout</div>
                  <div className="text-sm text-gray-600">30 minutes</div>
                </div>
              </div>
              <button className="text-pink-600 hover:text-pink-700 font-medium">Change</button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">API Configuration</h3>
          <div className="space-y-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-900">API Key</div>
                <Zap className="w-5 h-5 text-yellow-500" />
              </div>
              <div className="text-sm text-gray-600 mb-3">Access key for external integrations</div>
              <div className="flex items-center space-x-2">
                <input 
                  type="password" 
                  value="sk-1234567890abcdef" 
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50" 
                  readOnly 
                />
                <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                  Copy
                </button>
              </div>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-900">Webhook URL</div>
                <Globe className="w-5 h-5 text-blue-500" />
              </div>
              <div className="text-sm text-gray-600 mb-3">Endpoint for real-time notifications</div>
              <input 
                type="url" 
                placeholder="https://your-domain.com/webhook" 
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent" 
              />
            </div>
          </div>
        </div>
      </div>
      */}
    </div>
  );

  const renderHelp = () => (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-pink-600 via-teal-500 to-cyan-400 rounded-2xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">Help & Support</h1>
        <p className="text-pink-100 text-lg">Get assistance and find answers to common questions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-pink-500 to-pink-600 rounded-full mb-4">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Documentation</h3>
          <p className="text-gray-600 mb-4">Comprehensive guides and tutorials for using the dashboard</p>
          <button className="w-full bg-gradient-to-r from-pink-600 to-teal-600 text-white py-2 px-4 rounded-lg hover:from-pink-700 hover:to-teal-700 transition-all duration-200 flex items-center justify-center">
            <ExternalLink className="w-4 h-4 mr-2" />
            View Docs
          </button>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-teal-500 to-teal-600 rounded-full mb-4">
            <Video className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Video Tutorials</h3>
          <p className="text-gray-600 mb-4">Step-by-step video guides for common tasks</p>
          <button className="w-full bg-gradient-to-r from-pink-600 to-teal-600 text-white py-2 px-4 rounded-lg hover:from-pink-700 hover:to-teal-700 transition-all duration-200 flex items-center justify-center">
            <Video className="w-4 h-4 mr-2" />
            Watch Videos
          </button>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-full mb-4">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Live Chat</h3>
          <p className="text-gray-600 mb-4">Get instant help from our support team</p>
          <button className="w-full bg-gradient-to-r from-pink-600 to-teal-600 text-white py-2 px-4 rounded-lg hover:from-pink-700 hover:to-teal-700 transition-all duration-200 flex items-center justify-center">
            <MessageCircle className="w-4 h-4 mr-2" />
            Start Chat
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h3>
          <div className="space-y-4">
            {[
              {
                question: "How do I add a new researcher to the system?",
                answer: "Click the 'Add Researcher' button in the Researchers section and fill out the required information including name, contact details, and assignment."
              },
              {
                question: "How can I track survey completion progress?",
                answer: "Navigate to the Survey Status page where you can see real-time progress for each researcher, including completion percentages and status updates."
              },
              {
                question: "How do I export survey data?",
                answer: "You can export data by clicking the 'Export CSV' button in the main dashboard or going to Settings {'>'}  Data Export."
              }
            ].map((faq, index) => (
              <div key={index} className="border border-gray-200 rounded-lg">
                <button className="w-full text-left p-4 focus:outline-none focus:ring-2 focus:ring-pink-500 rounded-lg">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{faq.question}</h4>
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  </div>
                </button>
                <div className="px-4 pb-4">
                  <p className="text-sm text-gray-600">{faq.answer}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Contact Support</h3>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center mb-2">
                <Mail className="w-5 h-5 text-gray-600 mr-2" />
                <span className="font-medium text-gray-900">Email Support</span>
              </div>
              <p className="text-sm text-gray-600 mb-2">Get help via email within 24 hours</p>
              <a href="mailto:connect@wmefi.co.in" className="text-pink-600 hover:text-pink-700 font-medium">
                connect@wmefi.co.in
              </a>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center mb-2">
                <Phone className="w-5 h-5 text-gray-600 mr-2" />
                <span className="font-medium text-gray-900">Phone Support</span>
              </div>
              <p className="text-sm text-gray-600 mb-2">Call us during business hours</p>
              <a href="tel:+91919920154297" className="text-pink-600 hover:text-pink-700 font-medium">
                +91 919920154297
              </a>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center mb-2">
                <Clock className="w-5 h-5 text-gray-600 mr-2" />
                <span className="font-medium text-gray-900">Business Hours</span>
              </div>
              <p className="text-sm text-gray-600">Monday - Friday: 9:00 AM - 6:00 PM EST</p>
              <p className="text-sm text-gray-600">Saturday: 10:00 AM - 4:00 PM EST</p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gradient-to-r from-pink-50 to-teal-50 rounded-lg border border-pink-200">
            <h4 className="font-medium text-gray-900 mb-2">System Status</h4>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-sm text-gray-600">All systems operational</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard': return renderDashboard();
      case 'analytics': return renderAnalytics();
      case 'researchers': return renderResearchers();
      case 'survey-status': return renderSurveyStatus();
      case 'schedule': return renderSchedule();
      case 'settings': return renderSettings();
      case 'help': return renderHelp();
      default: return renderDashboard();
    }
  };

  return (
    <div className={`flex h-screen transition-colors duration-300 ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow-xl transition-all duration-300 flex flex-col border-r`}>
        <div className={`p-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <div className="flex items-center">
                <img 
                  src="/logo.png" 
                  alt="WMEFI Logo" 
                  className="w-10 h-10 rounded-xl mr-3 object-cover"
                />
                <div>
                  <h2 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>WMEFI</h2>
                  <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Access Dashboard</p>
                </div>
              </div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className={`p-2 rounded-lg transition-colors duration-200 ${darkMode ? 'hover:bg-gray-700 text-white' : 'hover:bg-gray-100 text-gray-900'}`}
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {sidebarItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => setCurrentPage(item.id)}
                  className={`w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 ${
                    currentPage === item.id
                      ? 'bg-gradient-to-r from-pink-600 to-teal-600 text-white shadow-lg'
                      : darkMode 
                        ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {sidebarOpen && <span className="ml-3 font-medium">{item.label}</span>}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {sidebarOpen && (
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-teal-500 rounded-full flex items-center justify-center text-white font-semibold mr-3">
                A
              </div>
              <div>
                <div className="font-medium text-gray-900">Admin User</div>
                <div className="text-sm text-gray-500">View Only Access</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {renderCurrentPage()}
        </div>
      </div>
    </div>
  );
};

export default App;