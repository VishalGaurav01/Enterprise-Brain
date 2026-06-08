import { useEffect, useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import api from '../lib/api';
import { Play, Plus } from 'lucide-react';

export default function RuleEngine() {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // New Rule State
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleExpr, setNewRuleExpr] = useState('');
  const [newRuleDesc, setNewRuleDesc] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);

  // Eval State
  const [evalRuleName, setEvalRuleName] = useState('');
  const [evalEmpId, setEvalEmpId] = useState('');
  const [evalResult, setEvalResult] = useState<any>(null);
  const [evalDialog, setEvalDialog] = useState(false);

  const fetchRules = async () => {
    try {
      const res = await api.get('/analytics/rules');
      setRules(res.data);
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
      await api.post('/analytics/rules', {
        rule_name: newRuleName,
        expression: newRuleExpr,
        description: newRuleDesc
      });
      setDialogOpen(false);
      setNewRuleName('');
      setNewRuleExpr('');
      setNewRuleDesc('');
      fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/analytics/evaluate', {
        rule_name: evalRuleName,
        employee_id: evalEmpId || undefined,
        is_organization: !evalEmpId
      });
      setEvalResult(res.data);
    } catch (err) {
      console.error(err);
      setEvalResult({ error: "Evaluation failed. Check ID." });
    }
  };

  const openEval = (ruleName: string) => {
    setEvalRuleName(ruleName);
    setEvalResult(null);
    setEvalEmpId('');
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
                <Label>Mathematical Expression</Label>
                <Input value={newRuleExpr} onChange={e => setNewRuleExpr(e.target.value)} placeholder="e.g. (Attributed_Revenue * 0.1) + 500" required className="font-mono" />
                <p className="text-xs text-muted-foreground">Available variables contextually injected.</p>
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Input value={newRuleDesc} onChange={e => setNewRuleDesc(e.target.value)} placeholder="What does this calculate?" />
              </div>
              <div className="pt-4 flex justify-end">
                <Button type="submit">Save Configuration</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-card/50 backdrop-blur-sm border-white/5">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rule Name</TableHead>
              <TableHead>Expression</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rules.map((r) => (
              <TableRow key={r.id}>
                <TableCell className="font-medium">{r.rule_name}</TableCell>
                <TableCell><code className="px-2 py-1 bg-secondary rounded text-xs text-primary">{r.expression}</code></TableCell>
                <TableCell className="text-muted-foreground">{r.description}</TableCell>
                <TableCell>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${r.is_active ? 'bg-green-500/10 text-green-500' : 'bg-destructive/10 text-destructive'}`}>
                    {r.is_active ? 'Active' : 'Inactive'}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="outline" size="sm" onClick={() => openEval(r.rule_name)} className="gap-2">
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
                <Label>Target Employee ID (Optional)</Label>
                <Input value={evalEmpId} onChange={e => setEvalEmpId(e.target.value)} placeholder="Leave blank for Org level" />
              </div>
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
