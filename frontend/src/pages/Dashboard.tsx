import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { TrendingUp, Users, FolderKanban, DollarSign, Activity } from 'lucide-react';
import { EmployeeService, ProjectService, AnalyticsService } from '../services';

export default function Dashboard() {
  const [orgMetrics, setOrgMetrics] = useState<any>(null);
  const [kpis, setKpis] = useState({ projectsCount: 0, teamCount: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Only doing lightweight API fetches, removing the N+1 computation
        const [orgRes, projects, employees] = await Promise.all([
          AnalyticsService.evaluate({
            rule_name: 'org_margin_v1',
            entity_type: 'organization',
            is_organization: true
          }),
          ProjectService.getProjects(),
          EmployeeService.getEmployees()
        ]);
        
        setOrgMetrics(orgRes.details);
        setKpis({
          projectsCount: projects.length,
          teamCount: employees.length
        });

      } catch (err) {
        console.error("Failed to fetch metrics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center min-h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin w-10 h-10 border-4 border-primary border-t-transparent rounded-full shadow-lg" />
          <p className="text-sm text-muted-foreground animate-pulse">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-10">
      
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Organization Overview
        </h1>
        <p className="text-muted-foreground">Welcome back. Here's what's happening today.</p>
      </div>

      {/* Top Stats Row */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        
        <Card className="bg-gradient-to-br from-card to-card/50 border-border/50 shadow-sm hover:shadow-md transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Revenue</CardTitle>
            <div className="w-10 h-10 bg-green-500/10 text-green-500 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <DollarSign className="w-5 h-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground">{formatCurrency(orgMetrics?.Total_Revenue)}</div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1.5 font-medium">
              <TrendingUp className="w-3.5 h-3.5 text-green-500" /> <span className="text-green-500">+12.5%</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/50 border-border/50 shadow-sm hover:shadow-md transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Investment</CardTitle>
            <div className="w-10 h-10 bg-orange-500/10 text-orange-500 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <Activity className="w-5 h-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground">{formatCurrency(orgMetrics?.Total_Investment)}</div>
            <p className="text-xs text-muted-foreground mt-2 font-medium">
              Salaries, Tools, & Vendors
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/50 border-border/50 shadow-sm hover:shadow-md transition-all duration-300 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Net Margin</CardTitle>
            <div className="w-10 h-10 bg-blue-500/10 text-blue-500 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <TrendingUp className="w-5 h-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className={`text-4xl font-bold tracking-tight ${orgMetrics?.Margin < 0 ? 'text-destructive' : 'text-blue-500'}`}>
              {formatCurrency(orgMetrics?.Margin)}
            </div>
            <p className="text-xs text-muted-foreground mt-2 font-medium">
              Overall Profitability
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/50 border-border/50 shadow-sm hover:shadow-md transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Projects</CardTitle>
            <div className="w-10 h-10 bg-purple-500/10 text-purple-500 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <FolderKanban className="w-5 h-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground">{kpis.projectsCount}</div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1.5 font-medium">
              <Users className="w-3.5 h-3.5 text-muted-foreground" /> {kpis.teamCount} Active Team Members
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Expanded Breakdown Row */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="bg-card border-border/50 shadow-sm md:col-span-2 lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-xl">Investment Breakdown</CardTitle>
            <CardDescription>Global allocation of capital resources</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4 pt-4">
              
              <div className="space-y-3 p-4 rounded-xl bg-secondary/30 border border-border/30">
                <div className="flex flex-col gap-1">
                  <span className="text-sm font-medium text-muted-foreground">Salaries</span>
                  <span className="text-2xl font-bold">{formatCurrency(orgMetrics?.Total_Salary)}</span>
                </div>
                <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all duration-1000" style={{ width: `${(orgMetrics?.Total_Salary / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-3 p-4 rounded-xl bg-secondary/30 border border-border/30">
                <div className="flex flex-col gap-1">
                  <span className="text-sm font-medium text-muted-foreground">Software Tools</span>
                  <span className="text-2xl font-bold">{formatCurrency(orgMetrics?.Total_Tools_Cost)}</span>
                </div>
                <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full transition-all duration-1000" style={{ width: `${(orgMetrics?.Total_Tools_Cost / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-3 p-4 rounded-xl bg-secondary/30 border border-border/30">
                <div className="flex flex-col gap-1">
                  <span className="text-sm font-medium text-muted-foreground">Vendor Costs</span>
                  <span className="text-2xl font-bold">{formatCurrency(orgMetrics?.Total_Project_Costs)}</span>
                </div>
                <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-orange-500 rounded-full transition-all duration-1000" style={{ width: `${(orgMetrics?.Total_Project_Costs / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>

              <div className="space-y-3 p-4 rounded-xl bg-secondary/30 border border-border/30">
                <div className="flex flex-col gap-1">
                  <span className="text-sm font-medium text-muted-foreground">Reimbursements</span>
                  <span className="text-2xl font-bold">{formatCurrency(orgMetrics?.Total_Reimbursements)}</span>
                </div>
                <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full transition-all duration-1000" style={{ width: `${(orgMetrics?.Total_Reimbursements / orgMetrics?.Total_Investment) * 100}%` }} />
                </div>
              </div>

            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
