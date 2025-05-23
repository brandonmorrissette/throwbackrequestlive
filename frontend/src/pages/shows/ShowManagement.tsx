import { Tab, TabList, TabPanel, Tabs } from 'react-tabs';
import RequestDashboard from '../request/RequestDashboard';
import ShowCreation from './ShowCreation';

/**
 * ShowManagement component that allows managing show tables.
 * @component
 */
const ShowManagement: React.FC = () => {
    return (
        <div>
            <Tabs>
                <TabList>
                    <Tab>Request Dashboard</Tab>
                    <Tab>Show Creation</Tab>
                </TabList>

                <TabPanel>
                    <RequestDashboard />
                </TabPanel>
                <TabPanel>
                    <ShowCreation />
                </TabPanel>
            </Tabs>
        </div>
    );
};

export default ShowManagement;
