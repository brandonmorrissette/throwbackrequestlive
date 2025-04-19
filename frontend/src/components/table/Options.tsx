import { ColDef } from './ColDef';

/**
 * Class representing the options for the table.
 */
export class Options {
    name: string;
    columns: ColDef[];
    primaryKeys: ColDef[];

    /**
     * Creates an instance of Options.
     * @param {string} name - The name of the table.
     * @param {ColDef[]} columns - The column definitions for the table.
     * @param {ColDef[]} [primaryKeys] - The primary key columns for the table.
     * @param {...any[]} additionalProps - Additional properties for the table.
     */
    constructor(
        name: string,
        columns: ColDef[],
        primaryKeys?: ColDef[],
        ...additionalProps: any[]
    ) {
        this.name = name;
        this.columns = columns;
        console.log('Properties::constructor::columns:', columns);
        this.primaryKeys = primaryKeys || [];

        additionalProps.forEach((prop) => {
            Object.entries(prop).forEach(([key, value]) => {
                if (!(key in this)) {
                    (this as any)[key] = value;
                } else {
                    console.log('Property already exists:', key);
                }
            });
        });
        console.log('Properties::constructor::properties:', this);
    }
}
