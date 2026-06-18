import React from 'react';
import { GraphVisualizer } from '../components/GraphVisualizer';

export const GraphPage: React.FC = () => {
    return (
        <div className="p-6 h-full flex flex-col gap-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">Knowledge Graph</h1>
                    <p className="text-gray-500 mt-1">Visualize the relationships between employees, departments, and projects.</p>
                </div>
            </div>
            
            <div className="flex-1 min-h-[600px] w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                <GraphVisualizer />
            </div>
        </div>
    );
};
