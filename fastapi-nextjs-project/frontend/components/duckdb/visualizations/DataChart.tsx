import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';
import PieChartIcon from '@mui/icons-material/PieChart';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import ScatterPlotIcon from '@mui/icons-material/ScatterPlot';
import dynamic from 'next/dynamic';

// Dynamically import the chart components to avoid SSR issues
const Chart = dynamic(
  () => import('react-apexcharts'),
  { ssr: false }
);

interface DataChartProps {
  data: any[];
}

const DataChart: React.FC<DataChartProps> = ({ data }) => {
  const [chartType, setChartType] = useState<string>('bar');
  const [xAxis, setXAxis] = useState<string>('');
  const [yAxis, setYAxis] = useState<string>('');
  const [columns, setColumns] = useState<string[]>([]);
  const [numericColumns, setNumericColumns] = useState<string[]>([]);
  const [chartOptions, setChartOptions] = useState<any>({});
  const [chartSeries, setChartSeries] = useState<any[]>([]);

  // Initialize columns and chart options on data change
  useEffect(() => {
    if (data && data.length > 0) {
      // Get columns from the first row
      const allColumns = Object.keys(data[0]);
      setColumns(allColumns);
      
      // Identify numeric columns
      const numeric = allColumns.filter(column => {
        const value = data[0][column];
        return typeof value === 'number';
      });
      setNumericColumns(numeric);
      
      // Set default axes if not already set
      if (!xAxis && allColumns.length > 0) {
        setXAxis(allColumns[0]);
      }
      
      if (!yAxis && numeric.length > 0) {
        setYAxis(numeric[0]);
      }
    }
  }, [data]);

  // Update chart options and series when axes or chart type changes
  useEffect(() => {
    if (!data || data.length === 0 || !xAxis || !yAxis) {
      return;
    }
    
    // Prepare data for the chart
    const categories = data.map(row => String(row[xAxis]));
    const series = [
      {
        name: yAxis,
        data: data.map(row => row[yAxis])
      }
    ];
    
    // Set chart options based on chart type
    let options: any = {
      chart: {
        type: chartType,
        height: 350,
        toolbar: {
          show: true
        }
      },
      xaxis: {
        categories,
        title: {
          text: xAxis
        }
      },
      yaxis: {
        title: {
          text: yAxis
        }
      },
      title: {
        text: `${yAxis} by ${xAxis}`,
        align: 'center'
      },
      tooltip: {
        enabled: true
      }
    };
    
    // Customize options for specific chart types
    if (chartType === 'pie') {
      options = {
        ...options,
        labels: categories,
        legend: {
          position: 'bottom'
        }
      };
      
      // For pie charts, we need a different series format
      series = [{
        data: data.map(row => row[yAxis])
      }];
    } else if (chartType === 'scatter') {
      // For scatter plots, we need x and y values
      series = [{
        name: `${xAxis} vs ${yAxis}`,
        data: data.map(row => ({
          x: row[xAxis],
          y: row[yAxis]
        }))
      }];
    }
    
    setChartOptions(options);
    setChartSeries(series);
  }, [data, xAxis, yAxis, chartType]);

  // Handle chart type change
  const handleChartTypeChange = (event: React.MouseEvent<HTMLElement>, newType: string) => {
    if (newType !== null) {
      setChartType(newType);
    }
  };

  // Check if the data is empty
  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No data to display
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>X-Axis</InputLabel>
            <Select
              value={xAxis}
              onChange={(e) => setXAxis(e.target.value)}
              label="X-Axis"
            >
              {columns.map((column) => (
                <MenuItem key={column} value={column}>
                  {column}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Y-Axis</InputLabel>
            <Select
              value={yAxis}
              onChange={(e) => setYAxis(e.target.value)}
              label="Y-Axis"
            >
              {numericColumns.map((column) => (
                <MenuItem key={column} value={column}>
                  {column}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={handleChartTypeChange}
            aria-label="chart type"
            size="small"
          >
            <ToggleButton value="bar" aria-label="bar chart">
              <BarChartIcon />
            </ToggleButton>
            <ToggleButton value="line" aria-label="line chart">
              <ShowChartIcon />
            </ToggleButton>
            <ToggleButton value="pie" aria-label="pie chart">
              <PieChartIcon />
            </ToggleButton>
            <ToggleButton value="scatter" aria-label="scatter plot">
              <ScatterPlotIcon />
            </ToggleButton>
          </ToggleButtonGroup>
        </Grid>
      </Grid>
      
      <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        {xAxis && yAxis && chartOptions.chart ? (
          <Chart
            options={chartOptions}
            series={chartSeries}
            type={chartType}
            height="100%"
            width="100%"
          />
        ) : (
          <Typography variant="body1" color="text.secondary">
            Select X and Y axes to display a chart
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default DataChart;
