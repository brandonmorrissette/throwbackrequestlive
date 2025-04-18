import React from 'react';
import { Bar } from 'react-chartjs-2';

/**
 * Dashboard Base Class
 *
 * This class provides shared logic for managing colors, chart options, and rendering.
 * It is intended to be extended by specific dashboard components.
 */
export class Dashboard {
    protected chartRef: React.RefObject<any>;
    protected data: any;
    protected syncFunction: () => void;
    protected options: any;

    constructor(
        chartRef: React.RefObject<any>,
        data: any,
        syncFunction: () => void,
        options?: any
    ) {
        this.chartRef = chartRef;
        this.data = data;
        this.syncFunction = syncFunction;
        this.options =
            options || this.getDefaultOptions(this.getPrimaryColorOpacity());

        const accentColor = this.getAccentColor();
        const primaryColor = this.getPrimaryColor();
        this.data.datasets = this.data.datasets.map((dataset: any) => ({
            ...dataset,
            backgroundColor: dataset.backgroundColor || accentColor,
            borderColor: dataset.borderColor || primaryColor,
        }));
    }

    /**
     * Retrieves the primary color from CSS variables.
     *
     * @returns The primary color as a string.
     */
    getPrimaryColor(): string {
        return getComputedStyle(document.documentElement)
            .getPropertyValue('--color-primary')
            .trim();
    }

    /**
     * Retrieves the primary color opacity from CSS variables.
     *
     * @returns The primary color opacity as a string.
     */
    getPrimaryColorOpacity(): string {
        return getComputedStyle(document.documentElement).getPropertyValue(
            '--color-primary-opacity'
        );
    }

    /**
     * Retrieves the accent color from CSS variables.
     *
     * @returns The accent color as a string.
     */
    getAccentColor(): string {
        return getComputedStyle(document.documentElement).getPropertyValue(
            '--color-accent'
        );
    }

    /**
     * Generates default chart options.
     *
     * @param color - The color to be used for chart ticks.
     * @returns An object containing the default chart options.
     */
    getDefaultOptions(color: string): any {
        return {
            scales: {
                x: {
                    ticks: {
                        color: color,
                        font: {
                            size: 18,
                        },
                    },
                },
                y: {
                    ticks: {
                        color: color,
                        stepSize: 1,
                        beginAtZero: true,
                    },
                },
            },
            plugins: {
                legend: {
                    display: false,
                },
            },
        };
    }

    /**
     * Renders the chart. This method can be overridden by child classes to customize the chart type.
     *
     * @returns A JSX element representing the chart.
     */
    renderChart(): JSX.Element {
        return <div>NOT IMPLEMENTED</div>;
    }

    /**
     * Renders the dashboard, including the sync button and chart.
     *
     * @returns A JSX element representing the dashboard.
     */
    render(): JSX.Element {
        return (
            <div style={{ marginTop: 20 }}>
                <button
                    id="syncButton"
                    onClick={this.syncFunction}
                    style={{
                        marginBottom: 10,
                        padding: '5px 10px',
                        cursor: 'pointer',
                    }}
                >
                    Sync
                </button>
                {this.renderChart()}
            </div>
        );
    }
}

/**
 * BarDashboard Component
 *
 * This functional component extends the `Dashboard` class to render a bar chart.
 */
export const BarDashboard: React.FC<{
    chartRef: React.RefObject<any>;
    data: any;
    syncFunction: () => void;
    options?: any;
}> = ({ chartRef, data, syncFunction, options }) => {
    class BarDashboardClass extends Dashboard {
        renderChart(): JSX.Element {
            return (
                <Bar
                    ref={this.chartRef}
                    data={this.data}
                    options={this.options}
                />
            );
        }
    }

    const dashboard = new BarDashboardClass(
        chartRef,
        data,
        syncFunction,
        options
    );
    return dashboard.render();
};
