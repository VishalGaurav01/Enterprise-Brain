import { useEffect, useState } from 'react';
import { EmployeeService, ProjectService } from '../services';
import type { Employee, Project, Department, Assignment } from '../types';
import { Card, CardContent } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Users, FolderKanban, Building2 } from 'lucide-react';

export default function Entities() {
  const [activeTab, setActiveTab] = useState<'employees' | 'projects' | 'departments'>('employees');
  
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [selectedEntity, setSelectedEntity] = useState<any>(null);
  const [entityType, setEntityType] = useState<'employee' | 'project' | 'department' | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [empList, projList, deptList] = await Promise.all([
        EmployeeService.getEmployees(),
        ProjectService.getProjects(),
        EmployeeService.getDepartments()
      ]);
      setEmployees(empList);
      setProjects(projList);
      setDepartments(deptList);
    } catch (err) {
      console.error("Error fetching entities", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loadingRelations, setLoadingRelations] = useState(false);

  const openDetails = async (type: 'employee' | 'project' | 'department', entity: any) => {
    setEntityType(type);
    setSelectedEntity(entity);
    setAssignments([]);
    
    if (type === 'employee') {
      setLoadingRelations(true);
      try {
        const assigned = await ProjectService.getAssignmentsByEmployee(entity.id);
        setAssignments(assigned);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingRelations(false);
      }
    } else if (type === 'project') {
      setLoadingRelations(true);
      try {
        const allAssigned = await ProjectService.getAssignments();
        setAssignments(allAssigned.filter((a: Assignment) => a.project_id === entity.id));
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingRelations(false);
      }
    }
  };

  const getDepartmentName = (deptId?: string) => {
    if (!deptId) return 'Unknown';
    const dept = departments.find(d => d.id === deptId);
    return dept ? dept.name : 'Unknown';
  };

  const getProjectName = (projId: string) => {
    const proj = projects.find(p => p.id === projId);
    return proj ? proj.name : 'Unknown';
  };
  
  const getEmployeeName = (empId: string) => {
    const emp = employees.find(e => e.id === empId);
    return emp ? `${emp.first_name} ${emp.last_name}` : 'Unknown';
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Entity Explorer</h2>
        <p className="text-muted-foreground">View and explore relations across all organizational entities.</p>
      </div>

      {/* Custom Tabs */}
      <div className="flex gap-4 border-b border-white/10 pb-4">
        <Button 
          variant={activeTab === 'employees' ? 'default' : 'ghost'} 
          className="gap-2" 
          onClick={() => setActiveTab('employees')}
        >
          <Users className="w-4 h-4" /> Employees
        </Button>
        <Button 
          variant={activeTab === 'projects' ? 'default' : 'ghost'} 
          className="gap-2" 
          onClick={() => setActiveTab('projects')}
        >
          <FolderKanban className="w-4 h-4" /> Projects
        </Button>
        <Button 
          variant={activeTab === 'departments' ? 'default' : 'ghost'} 
          className="gap-2" 
          onClick={() => setActiveTab('departments')}
        >
          <Building2 className="w-4 h-4" /> Departments
        </Button>
      </div>

      <Card className="bg-card border-border">
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">Loading entities...</div>
          ) : (
            <div className="overflow-x-auto">
              {activeTab === 'employees' && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Department</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {employees.map(e => (
                      <TableRow key={e.id}>
                        <TableCell className="font-medium">{e.first_name} {e.last_name}</TableCell>
                        <TableCell>{e.email}</TableCell>
                        <TableCell>{e.designation_id || 'Employee'}</TableCell>
                        <TableCell>{getDepartmentName(e.department_id)}</TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm" onClick={() => openDetails('employee', e)}>
                            View Relations
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}

              {activeTab === 'projects' && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Project Name</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Budget</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {projects.map(p => (
                      <TableRow key={p.id}>
                        <TableCell className="font-medium">{p.name}</TableCell>
                        <TableCell>
                           <span className={`px-2 py-1 rounded text-xs ${p.status === 'active' ? 'bg-green-500/10 text-green-500' : 'bg-secondary text-muted-foreground'}`}>
                             {p.status || 'Active'}
                           </span>
                        </TableCell>
                        <TableCell>${p.budget_allocated?.toLocaleString() || 0}</TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm" onClick={() => openDetails('project', p)}>
                            View Relations
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}

              {activeTab === 'departments' && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Department Name</TableHead>
                      <TableHead>Head (Manager ID)</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {departments.map(d => (
                      <TableRow key={d.id}>
                        <TableCell className="font-medium">{d.name}</TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">{d.manager_id || 'N/A'}</TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm" onClick={() => openDetails('department', d)}>
                            View Relations
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Relations Dialog */}
      <Dialog open={!!selectedEntity} onOpenChange={(open) => !open && setSelectedEntity(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {entityType === 'employee' && <Users className="w-5 h-5" />}
              {entityType === 'project' && <FolderKanban className="w-5 h-5" />}
              {entityType === 'department' && <Building2 className="w-5 h-5" />}
              Relation Details
            </DialogTitle>
          </DialogHeader>
          
          <div className="pt-4">
            {entityType === 'employee' && selectedEntity && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold">{selectedEntity.first_name} {selectedEntity.last_name}</h3>
                <div className="grid grid-cols-2 gap-4">
                   <div className="bg-secondary p-3 rounded-lg border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Belongs To Department</div>
                      <div className="font-medium text-primary">{getDepartmentName(selectedEntity.department_id)}</div>
                   </div>
                   <div className="bg-secondary p-3 rounded-lg border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Assigned Projects</div>
                      <div className="font-medium text-muted-foreground">
                        {loadingRelations ? 'Loading...' : (
                          assignments.length > 0 ? (
                            <ul className="list-disc pl-4 space-y-1 mt-1 text-sm">
                              {assignments.map(a => (
                                <li key={a.id} className="text-foreground">
                                  {getProjectName(a.project_id)} ({a.allocation_percentage}%)
                                </li>
                              ))}
                            </ul>
                          ) : 'No projects assigned'
                        )}
                      </div>
                   </div>
                </div>
              </div>
            )}

            {entityType === 'project' && selectedEntity && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold">{selectedEntity.name}</h3>
                <div className="grid grid-cols-2 gap-4">
                   <div className="bg-secondary p-3 rounded-lg border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Budget</div>
                      <div className="font-medium">${selectedEntity.budget?.toLocaleString()}</div>
                   </div>
                   <div className="bg-secondary p-3 rounded-lg border border-white/5 max-h-48 overflow-y-auto">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Assigned Employees</div>
                      <div className="font-medium text-muted-foreground">
                        {loadingRelations ? 'Loading...' : (
                          assignments.length > 0 ? (
                            <ul className="list-disc pl-4 space-y-1 mt-1 text-sm">
                              {assignments.map(a => (
                                <li key={a.id} className="text-foreground">
                                  {getEmployeeName(a.employee_id)} ({a.allocation_percentage}%)
                                </li>
                              ))}
                            </ul>
                          ) : 'No employees assigned'
                        )}
                      </div>
                   </div>
                </div>
              </div>
            )}

            {entityType === 'department' && selectedEntity && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold">{selectedEntity.name}</h3>
                <div className="bg-secondary p-4 rounded-lg border border-white/5">
                  <div className="text-xs text-muted-foreground uppercase mb-2">Employees in {selectedEntity.name}</div>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {employees.filter(e => e.department_id === selectedEntity.id).map(emp => (
                      <div key={emp.id} className="text-sm font-medium">
                         - {emp.first_name} {emp.last_name}
                      </div>
                    ))}
                    {employees.filter(e => e.department_id === selectedEntity.id).length === 0 && (
                      <div className="text-sm text-muted-foreground">No employees found.</div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

    </div>
  );
}
