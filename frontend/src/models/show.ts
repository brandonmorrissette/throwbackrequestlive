/**
 * Class representing a Show.
 */
export class Show {
    id: string;
    name: string;
    start_time: string;
    end_time: string;
    venue: string;
    street: string;
    city: string;
    state: string;

    /**
     * Create a Show.
     * @param {Show} show - The show data.
     */
    constructor(show: Show) {
        this.id = show.id;
        this.name = show.name;
        this.start_time = this.formatDateTime(show.start_time);
        this.end_time = this.formatDateTime(show.end_time);
        this.venue = show.venue;
        this.street = show.street;
        this.city = show.city;
        this.state = show.state;
    }

    /**
     * Format the datetime string.
     * @param {string} datetime - The datetime string to format.
     * @returns {string} The formatted datetime string.
     */
    private formatDateTime(datetime: string): string {
        const date = new Date(datetime);
        const formattedDate = date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: '2-digit',
            year: 'numeric',
        });
        const formattedTime = date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        });
        return `${formattedDate} ${formattedTime}`;
    }
}
