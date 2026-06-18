import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import api from '../lib/api';

interface GraphData {
    nodes: any[];
    links: any[];
}

export const GraphVisualizer: React.FC = () => {
    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [layoutMode, setLayoutMode] = useState<'td' | 'lr' | 'network'>('lr');

    useEffect(() => {
        // Resize observer to make graph responsive
        const observeTarget = containerRef.current;
        const resizeObserver = new ResizeObserver((entries) => {
            if (entries[0]) {
                const { width, height } = entries[0].contentRect;
                setDimensions({ width, height: height || 600 });
            }
        });

        if (observeTarget) {
            resizeObserver.observe(observeTarget);
        }

        return () => {
            if (observeTarget) {
                resizeObserver.unobserve(observeTarget);
            }
        };
    }, []);

    useEffect(() => {
        const fetchGraphData = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('Not authenticated');
                }

                const response = await api.get('/analytics/graph-data');
                const data = response.data;

                // Pre-process data to calculate degree for node sizing
                data.nodes.forEach((node: any) => {
                    const degree = data.links.filter(
                        (l: any) => l.source === node.id || l.target === node.id
                    ).length;
                    node.val = Math.max(degree * 1.5, 4); // Size based on connections
                });

                setGraphData(data);
                setLoading(false);
            } catch (err: any) {
                console.error("Failed to fetch graph data", err);
                setError(err.message || 'Failed to fetch graph data');
                setLoading(false);
            }
        };

        fetchGraphData();
    }, []);

    if (loading) {
        return <div className="flex items-center justify-center h-full w-full">Loading graph data...</div>;
    }

    if (error) {
        return <div className="text-red-500 p-4">Error: {error}</div>;
    }

    return (
        <div className="flex flex-col gap-4 w-full h-full">
            <div className="flex items-center justify-between bg-white dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Schema Explorer</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Interactive graph visualization of your organizational data.</p>
                </div>
                <div className="flex gap-2">
                    <button 
                        onClick={() => setLayoutMode('lr')}
                        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${layoutMode === 'lr' ? 'bg-primary text-primary-foreground' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
                    >
                        Folder View (L-R)
                    </button>
                    <button 
                        onClick={() => setLayoutMode('td')}
                        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${layoutMode === 'td' ? 'bg-primary text-primary-foreground' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
                    >
                        Hierarchical (T-D)
                    </button>
                    <button 
                        onClick={() => setLayoutMode('network')}
                        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${layoutMode === 'network' ? 'bg-primary text-primary-foreground' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
                    >
                        Network
                    </button>
                </div>
            </div>

            <div ref={containerRef} className="flex-1 min-h-[600px] border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden bg-white dark:bg-gray-950 shadow-sm relative">
                {graphData.nodes.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500">
                        <p>No graph data available.</p>
                        <p className="text-sm">Have you run the neo4j sync script?</p>
                    </div>
                ) : (
                    <ForceGraph2D
                        width={dimensions.width}
                        height={dimensions.height}
                        graphData={graphData}
                        dagMode={layoutMode === 'network' ? undefined : layoutMode}
                        dagLevelDistance={80}
                        nodeLabel={(node: any) => `${node.label}: ${node.properties?.name || node.properties?.first_name || node.id}`}
                        nodeColor={(node: any) => {
                            if (node.label === 'Employee') return '#3b82f6'; // blue
                            if (node.label === 'Department') return '#10b981'; // green
                            if (node.label === 'Project') return '#f59e0b'; // amber
                            return '#8b5cf6'; // purple for anything else
                        }}
                        nodeRelSize={6}
                        nodeCanvasObjectMode={() => 'after'}
                        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                            if (globalScale < 1.2) return; // Only show text when zoomed in
                            const label = node.properties?.name || node.properties?.first_name || node.id;
                            const fontSize = 12 / globalScale;
                            ctx.font = `${fontSize}px Sans-Serif`;
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillStyle = '#9ca3af'; // soft gray
                            const r = Math.sqrt(node.val || 1) * 6;
                            ctx.fillText(label, node.x, node.y + r + fontSize);
                        }}
                        linkColor={(link: any) => {
                            if (link.type === 'WORKS_IN') return '#3b82f655';
                            if (link.type === 'BELONGS_TO') return '#10b98155';
                            if (link.type === 'ASSIGNED_TO') return '#f59e0b55';
                            return '#6b728055';
                        }}
                        linkWidth={(link: any) => link.type === 'WORKS_IN' ? 2 : 1}
                        linkDirectionalArrowLength={3.5}
                        linkDirectionalArrowRelPos={1}
                        linkDirectionalParticles={2}
                        linkDirectionalParticleWidth={2}
                        linkCurvature={0.25}
                        linkLabel={(link: any) => link.type}
                        d3AlphaDecay={0.02}
                        d3VelocityDecay={0.3}
                    />
                )}
            </div>
        </div>
    );
};
