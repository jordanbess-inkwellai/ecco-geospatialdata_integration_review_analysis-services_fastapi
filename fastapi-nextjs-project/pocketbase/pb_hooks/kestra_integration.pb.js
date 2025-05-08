/// <reference path="../pb_data/types.d.ts" />

// Import required modules
const axios = require('axios');

// Define the Kestra API URL
const KESTRA_API_URL = process.env.KESTRA_API_URL || 'http://localhost:8080/api/v1';

// Function to trigger a Kestra workflow
async function triggerKestraWorkflow(namespace, flowId, inputs = {}) {
    try {
        const response = await axios.post(`${KESTRA_API_URL}/executions/trigger/${namespace}/${flowId}`, {
            inputs: inputs
        });
        
        return response.data;
    } catch (error) {
        console.error(`Error triggering Kestra workflow ${namespace}/${flowId}:`, error.message);
        throw error;
    }
}

// Function to get workflow execution status
async function getExecutionStatus(executionId) {
    try {
        const response = await axios.get(`${KESTRA_API_URL}/executions/${executionId}`);
        return response.data;
    } catch (error) {
        console.error(`Error getting execution status for ${executionId}:`, error.message);
        throw error;
    }
}

// Function to check if a record matches a filter
function recordMatchesFilter(record, filter) {
    if (!filter) return true;
    
    try {
        // Simple filter parser for basic conditions
        // Format: field operator value, e.g., "status = 'online'" or "connection_count > 10"
        const parts = filter.match(/(\w+)\s*([=!<>]+)\s*['"]?([^'"]+)['"]?/);
        if (!parts || parts.length !== 4) return true;
        
        const [_, field, operator, value] = parts;
        
        // Get the field value from the record
        const fieldValue = record.get(field);
        if (fieldValue === undefined) return false;
        
        // Compare based on operator
        switch (operator) {
            case '=':
            case '==':
                return String(fieldValue) === value;
            case '!=':
                return String(fieldValue) !== value;
            case '>':
                return Number(fieldValue) > Number(value);
            case '<':
                return Number(fieldValue) < Number(value);
            case '>=':
                return Number(fieldValue) >= Number(value);
            case '<=':
                return Number(fieldValue) <= Number(value);
            default:
                return false;
        }
    } catch (error) {
        console.error('Error evaluating filter:', error);
        return false;
    }
}

// Function to process a PocketBase event and trigger Kestra workflows
async function processPocketBaseEvent(collection, record, eventType) {
    try {
        // Find all triggers that match this event
        const triggers = $app.dao().findRecordsByFilter(
            'kestra_triggers',
            `trigger_type = 'pocketbase_event' && collection = '${collection}' && event_type = '${eventType}' && enabled = true`
        );
        
        for (const trigger of triggers) {
            // Check if the record matches the filter
            const filter = trigger.get('filter');
            if (!recordMatchesFilter(record, filter)) {
                continue;
            }
            
            // Get the workflow
            const workflowId = trigger.get('workflow');
            const workflow = $app.dao().findRecordById('kestra_workflows', workflowId);
            
            if (!workflow || !workflow.get('enabled')) {
                continue;
            }
            
            // Prepare inputs
            const inputs = {
                ...(trigger.get('inputs') || {}),
                event: {
                    collection: collection,
                    record_id: record.id,
                    event_type: eventType,
                    timestamp: new Date().toISOString(),
                    record_data: record.export()
                }
            };
            
            // Trigger the workflow
            const execution = await triggerKestraWorkflow(
                workflow.get('namespace'),
                workflow.get('workflow_id'),
                inputs
            );
            
            // Update the trigger's last_triggered timestamp
            trigger.set('last_triggered', new Date().toISOString());
            $app.dao().saveRecord(trigger);
            
            // Create an execution record
            const executionRecord = new Record($app.dao().findCollectionByNameOrId('kestra_executions'), {
                workflow: workflowId,
                execution_id: execution.id,
                namespace: execution.namespace,
                workflow_id: execution.flowId,
                status: execution.state,
                start_date: new Date().toISOString(),
                inputs: JSON.stringify(inputs),
                trigger: JSON.stringify({
                    id: trigger.id,
                    name: trigger.get('name'),
                    type: 'pocketbase_event',
                    collection: collection,
                    event_type: eventType
                })
            });
            
            $app.dao().saveRecord(executionRecord);
            
            console.log(`Triggered Kestra workflow ${workflow.get('namespace')}/${workflow.get('workflow_id')} with execution ID ${execution.id}`);
        }
    } catch (error) {
        console.error('Error processing PocketBase event:', error);
    }
}

// Function to process a database alert and trigger Kestra workflows
async function processDatabaseAlert(alert) {
    try {
        // Find all triggers that match this alert
        const triggers = $app.dao().findRecordsByFilter(
            'kestra_triggers',
            `trigger_type = 'database_alert' && enabled = true`
        );
        
        for (const trigger of triggers) {
            // Get the workflow
            const workflowId = trigger.get('workflow');
            const workflow = $app.dao().findRecordById('kestra_workflows', workflowId);
            
            if (!workflow || !workflow.get('enabled')) {
                continue;
            }
            
            // Prepare inputs
            const inputs = {
                ...(trigger.get('inputs') || {}),
                alert: {
                    id: alert.id,
                    database_id: alert.get('database'),
                    rule_id: alert.get('rule'),
                    status: alert.get('status'),
                    severity: alert.get('severity'),
                    message: alert.get('message'),
                    metric_value: alert.get('metric_value'),
                    triggered_at: alert.get('triggered_at')
                }
            };
            
            // Trigger the workflow
            const execution = await triggerKestraWorkflow(
                workflow.get('namespace'),
                workflow.get('workflow_id'),
                inputs
            );
            
            // Update the trigger's last_triggered timestamp
            trigger.set('last_triggered', new Date().toISOString());
            $app.dao().saveRecord(trigger);
            
            // Create an execution record
            const executionRecord = new Record($app.dao().findCollectionByNameOrId('kestra_executions'), {
                workflow: workflowId,
                execution_id: execution.id,
                namespace: execution.namespace,
                workflow_id: execution.flowId,
                status: execution.state,
                start_date: new Date().toISOString(),
                inputs: JSON.stringify(inputs),
                trigger: JSON.stringify({
                    id: trigger.id,
                    name: trigger.get('name'),
                    type: 'database_alert',
                    alert_id: alert.id,
                    severity: alert.get('severity')
                })
            });
            
            $app.dao().saveRecord(executionRecord);
            
            console.log(`Triggered Kestra workflow ${workflow.get('namespace')}/${workflow.get('workflow_id')} with execution ID ${execution.id} for alert ${alert.id}`);
        }
    } catch (error) {
        console.error('Error processing database alert:', error);
    }
}

// Hook: After a record is created
onModelAfterCreate((e) => {
    const collection = e.model.collection().name;
    
    // Skip Kestra collections to avoid infinite loops
    if (collection.startsWith('kestra_')) {
        return;
    }
    
    // Process the event
    processPocketBaseEvent(collection, e.model, 'create');
    
    // Special handling for alerts
    if (collection === 'alerts' && e.model.get('status') === 'triggered') {
        processDatabaseAlert(e.model);
    }
});

// Hook: After a record is updated
onModelAfterUpdate((e) => {
    const collection = e.model.collection().name;
    
    // Skip Kestra collections to avoid infinite loops
    if (collection.startsWith('kestra_')) {
        return;
    }
    
    // Process the event
    processPocketBaseEvent(collection, e.model, 'update');
    
    // Special handling for alerts
    if (collection === 'alerts') {
        const oldStatus = e.model.originalModel().get('status');
        const newStatus = e.model.get('status');
        
        // If status changed to triggered, process the alert
        if (oldStatus !== 'triggered' && newStatus === 'triggered') {
            processDatabaseAlert(e.model);
        }
    }
});

// Hook: After a record is deleted
onModelAfterDelete((e) => {
    const collection = e.model.collection().name;
    
    // Skip Kestra collections to avoid infinite loops
    if (collection.startsWith('kestra_')) {
        return;
    }
    
    // Process the event
    processPocketBaseEvent(collection, e.model, 'delete');
});

// Background task to update execution statuses
async function updateExecutionStatuses() {
    try {
        // Find all executions that are not in a terminal state
        const nonTerminalStates = ['CREATED', 'RUNNING', 'PAUSED', 'RESTARTED', 'KILLING'];
        const executions = $app.dao().findRecordsByFilter(
            'kestra_executions',
            `status IN ['${nonTerminalStates.join("','")}']`
        );
        
        for (const execution of executions) {
            try {
                // Get the current status from Kestra
                const executionId = execution.get('execution_id');
                const status = await getExecutionStatus(executionId);
                
                // Update the execution record
                execution.set('status', status.state);
                
                if (['SUCCESS', 'WARNING', 'FAILED', 'KILLED'].includes(status.state)) {
                    execution.set('end_date', new Date(status.state.endDate || Date.now()).toISOString());
                    
                    // Calculate duration
                    const startDate = new Date(status.startDate || execution.get('start_date'));
                    const endDate = new Date(status.endDate || Date.now());
                    const duration = endDate.getTime() - startDate.getTime();
                    execution.set('duration', duration);
                    
                    // Store outputs
                    if (status.outputs) {
                        execution.set('outputs', JSON.stringify(status.outputs));
                    }
                    
                    // Store task runs
                    if (status.taskRunList) {
                        execution.set('task_runs', JSON.stringify(status.taskRunList));
                    }
                }
                
                $app.dao().saveRecord(execution);
            } catch (error) {
                console.error(`Error updating execution ${execution.get('execution_id')}:`, error.message);
            }
        }
    } catch (error) {
        console.error('Error updating execution statuses:', error);
    }
    
    // Schedule the next update
    setTimeout(updateExecutionStatuses, 30000); // Run every 30 seconds
}

// Start the background task when the server starts
onServerStart(() => {
    // Wait a bit before starting the background task
    setTimeout(() => {
        updateExecutionStatuses();
    }, 10000);
});
