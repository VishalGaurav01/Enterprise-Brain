import { useEffect, useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { AnalyticsService } from '../services';
import type { BusinessRule } from '../types';
import { Play, Plus } from 'lucide-react';

export default function RuleEngine() {
  const [rules, setRules] = useState<BusinessRule[]>([]);
  const [loading, setLoading] = useState(true);

  // New Rule State
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleCondition, setNewRuleCondition] = useState('{"metric": "employee_roi", "operator": "<", "value": 20.0}');
  const [newRuleAction, setNewRuleAction] = useState('{"recommendation": "investigate", "severity": "medium"}');
  const [newRuleEntityType, setNewRuleEntityType] = useState('employee');
  const [dialogOpen, setDialogOpen] = useState(false);

  // Eval State
  const [evalRuleName, setEvalRuleName] = useState('');
  const [evalEntityType, setEvalEntityType] = useState('');
  const [evalEntityId, setEvalEntityId] = useState('');
  const [evalResult, setEvalResult] = useState<any>(null);
  const [evalDialog, setEvalDialog] = useState(false);

  const fetchRules = async () => {
    try {
      const res = await AnalyticsService.getRules();
      setRules(res);
    } catch (err) {
      console.error("Failed to fetch rules", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await AnalyticsService.createRule({
        rule_name: newRuleName,
        entity_type: newRuleEntityType,
        condition: JSON.parse(newRuleCondition),
        action: JSON.parse(newRuleAction),
        priority: 1,
        enabled: true
      });
      setDialogOpen(false);
      setNewRuleName('');
      fetchRules();
    } catch (err) {
      console.error(err);
      alert("Failed to create rule. Check JSON format.");
    }
  };

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        rule_name: evalRuleName,
        entity_type: evalEntityType,
        is_organization: evalEntityType === 'organization'
      };
      
      if (evalEntityId) {
        if (evalEntityType === 'employee') payload.employee_id = evalEntityId;
        if (evalEntityType === 'project') payload.project_id = evalEntityId;
        if (evalEntityType === 'department') payload.department_id = evalEntityId;
      }

      const res = await AnalyticsService.evaluate(payload);
      setEvalResult(res);
    } catch (err) {
      console.error(err);
      setEvalResult({ error: "Evaluation failed. Check ID." });
    }
  };

  const openEval = (rule: BusinessRule) => {
    setEvalRuleName(rule.rule_name);
    setEvalEntityType(rule.entity_type);
    setEvalResult(null);
    setEvalEntityId('');
    setEvalDialog(true);
  };

  if (loading) return <div>Loading rules...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Rule Engine Configurations</h2>
          <p className="text-muted-foreground">Manage dynamic formulas and calculations.</p>
        </div>
        
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="w-4 h-4"/> Create Rule</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Rule</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateRule} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Rule Name</Label>
                <Input value={newRuleName} onChange={e => setNewRuleName(e.target.value)} placeholder="e.g. custom_bonus_v1" required />
              </div>
              <div className="space-y-2">
                <Label>Entity Type</Label>
                <Input value={newRuleEntityType} onChange={e => setNewRuleEntityType(e.target.value)} placeholder="e.g. employee, project, organization" required />
              </div>
              <div className="space-y-2">
                <Label>Condition (JSON)</Label>
                <Input value={newRuleCondition} onChange={e => setNewRuleCondition(e.target.value)} placeholder='{"metric": "employee_roi", "operator": "<", "value": 20}' required className="font-mono" />
              </div>
              <div className="space-y-2">
                <Label>Action (JSON)</Label>
                <Input value={newRuleAction} onChange={e => setNewRuleAction(e.target.value)} placeholder='{"recommendation": "investigate"}' required className="font-mono" />
              </div>
              <div className="pt-4 flex justify-end">
                <Button type="submit">Save Configuration</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-card border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rule Name</TableHead>
              <TableHead>Entity Type</TableHead>
              <TableHead>Condition</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rules.map((r) => (
              <TableRow key={r.rule_id || r.rule_name}>
                <TableCell className="font-medium">{r.rule_name}</TableCell>
                <TableCell>{r.entity_type}</TableCell>
                <TableCell><code className="px-2 py-1 bg-secondary rounded text-xs text-primary">{JSON.stringify(r.condition)}</code></TableCell>
                <TableCell>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${r.enabled ? 'bg-green-500/10 text-green-500' : 'bg-destructive/10 text-destructive'}`}>
                    {r.enabled ? 'Active' : 'Inactive'}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="outline" size="sm" onClick={() => openEval(r)} className="gap-2">
                    <Play className="w-3 h-3" /> Test
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <Dialog open={evalDialog} onOpenChange={setEvalDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Evaluate Rule Sandbox</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-6 pt-4">
            <form onSubmit={handleEvaluate} className="space-y-4">
              <div className="space-y-2">
                <Label>Rule Name</Label>
                <Input value={evalRuleName} disabled className="bg-muted" />
              </div>
              <div className="space-y-2">
                <Label>Entity Type</Label>
                <Input value={evalEntityType} disabled className="bg-muted" />
              </div>
              {evalEntityType !== 'organization' && (
                <div className="space-y-2">
                  <Label>Target {evalEntityType} ID</Label>
                  <Input value={evalEntityId} onChange={e => setEvalEntityId(e.target.value)} placeholder={`Enter ${evalEntityType} UUID`} required />
                </div>
              )}
              <Button type="submit" className="w-full">Run Evaluation</Button>
            </form>

            <div className="bg-secondary/50 rounded-lg p-4 border border-white/5 h-full">
              <h4 className="font-medium text-sm mb-4 text-muted-foreground">Output Logs</h4>
              {evalResult ? (
                evalResult.error ? (
                  <div className="text-destructive text-sm">{evalResult.error}</div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Final Result</div>
                      <div className="text-2xl font-bold text-primary">{evalResult.result}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Injected Context Variables</div>
                      <pre className="text-[10px] bg-background/50 p-2 rounded border border-white/5 overflow-x-auto text-green-400">
                        {JSON.stringify(evalResult.details, null, 2)}
                      </pre>
                    </div>
                  </div>
                )
              ) : (
                <div className="text-sm text-muted-foreground">Waiting for execution...</div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
