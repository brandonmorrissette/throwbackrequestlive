import { ColDef } from './ColDef';

export class Options {
    name: string;
    columns: ColDef[];
    primaryKeys: ColDef[];

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
