import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, Users, FolderKanban, DollarSign, Activity } from 'lucide-react';
import { EmployeeService, ProjectService, AnalyticsService } from '../services';
import type { Department } from '../types';

export default function Dashboard() {
  const [orgMetrics, setOrgMetrics] = useState<any>(null);
  const [chartData, setChartData] = useState<{name: string, profit: number}[]>([]);
  const [kpis, setKpis] = useState({ projectsCount: 0, teamCount: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // 1. Fetch Org Level Metrics
        const orgRes = await AnalyticsService.evaluate({
          rule_name: 'org_margin_v1',
          entity_type: 'organization',
          is_organization: true
        });
        setOrgMetrics(orgRes.details);

        // 2. Fetch Base Entity Counts
        const [projects, employees, departments] = await Promise.all([
          ProjectService.getProjects(),
          EmployeeService.getEmployees(),
          EmployeeService.getDepartments()
        ]);
        
        setKpis({
          projectsCount: projects.length,
          teamCount: employees.length
        });

        // 3. Evaluate Department Profitability for Chart
        const deptPromises = departments.map(async (d: Department) => {
          try {
            const evalRes = await AnalyticsService.evaluate({
              rule_name: 'department_profit_v1',
              entity_type: 'department',
              department_id: d.id
            });
            return {
              name: d.name,
              profit: evalRes.result || 0
            };
          } catch (e) {
            return { name: d.name, profit: 0 };
          }
        });
        
        const chartResults = await Promise.all(deptPromises);
        setChartData(chartResults);

      } catch (err) {
        console.error("Failed to fetch metrics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return <div className="flex h-full items-center justify-center"><div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" /></div>;
  }

  const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0);



  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Top Stats Row */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-card border-border hover:border-border/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Revenue</CardTitle>
            <div className="w-8 h-8 bg-green-500/10 text-green-500 rounded-md flex items-center justify-center"><DollarSign className="w-4 h-4" /></div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tight">{formatCurrency(orgMetrics?.Total_Revenue)}</div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-green-500" /> +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border hover:border-border/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Investment</CardTitle>
            <div className="w-8 h-8 bg-orange-500/10 text-orange-500 rounded-md flex items-center justify-center"><Activity className="w-4 h-4" /></div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tight">{formatCurrency(orgMetrics?.Total_Investment)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Includes Salaries & Tools
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border hover:border-border/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Org Margin</CardTitle>
            <div className="w-8 h-8 bg-blue-500/10 text-blue-500 rounded-md flex items-center justify-center"><TrendingUp className="w-4 h-4" /></div>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold tracking-tight ${orgMetrics?.Margin < 0 ? 'text-destructive' : 'text-green-500'}`}>
              {formatCurrency(orgMetrics?.Margin)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Net Profitability
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border hover:border-border/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Projects</CardTitle>
            <div className="w-8 h-8 bg-purple-500/10 text-purple-500 rounded-md flex items-center justify-center"><FolderKanban className="w-4 h-4" /></div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tight">{kpis.projectsCount}</div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
              <Users className="w-3 h-3 text-muted-foreground" /> {kpis.teamCount} Team Members
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Department Profitability</CardTitle>
            <CardDescription>Net profit/loss by business unit</CardDescription>
          </CardHeader>
          <CardContent className="h-80 min-h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%" minHeight={300}>
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value / 1000}k`} />
                <Tooltip 
                  cursor={{fill: '#ffffff05'}}
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid #ffffff10', borderRadius: '8px' }}
                  formatter={(value: any) => formatCurrency(Number(value))}
                />
                <Bar dataKey="profit" radius={[4, 4, 4, 4]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.profit >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Investment Breakdown</CardTitle>
            <CardDescription>Where capital is allocated globally</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6 pt-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Salaries</span>
                  <span className="font-medium">{formatCurrency(orgMetrics?.Total_Salary)}</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${(orgMetrics?.Total_Salary / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Software Tools</span>
                  <span className="font-medium">{formatCurrency(orgMetrics?.Total_Tools_Cost)}</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500" style={{ width: `${(orgMetrics?.Total_Tools_Cost / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Vendor Costs</span>
                  <span className="font-medium">{formatCurrency(orgMetrics?.Total_Project_Costs)}</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-orange-500" style={{ width: `${(orgMetrics?.Total_Project_Costs / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Reimbursements</span>
                  <span className="font-medium">{formatCurrency(orgMetrics?.Total_Reimbursements)}</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500" style={{ width: `${(orgMetrics?.Total_Reimbursements / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
