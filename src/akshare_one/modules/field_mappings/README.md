# Field Mappings Configuration Directory

This directory contains JSON configuration files that define mappings between source data fields and standardized field names.

## File Naming Convention

Configuration files should follow the naming pattern: `{source}_{module}.json`

Examples:
- `eastmoney_fundflow.json` - Mappings for fundflow module from Eastmoney source
- `eastmoney_northbound.json` - Mappings for northbound module from Eastmoney source

## Configuration File Format

Each configuration file should be a JSON file with the following structure:

```json
{
  "source": "eastmoney",
  "module": "fundflow",
  "version": "1.0",
  "last_updated": "2024-01-01",
  "mappings": [
    {
      "source_field": "日期",
      "standard_field": "date",
      "field_type": "date",
      "description": "交易日期"
    },
    {
      "source_field": "主力净流入-净额",
      "standard_field": "main_net_inflow",
      "field_type": "net_flow",
      "source_unit": "yuan",
      "target_unit": "yuan",
      "description": "主力资金净流入金额"
    }
  ]
}
```

## Field Types

Valid field types include:
- `date` - Date fields (YYYY-MM-DD format)
- `timestamp` - Timestamp fields with timezone
- `event_date` - Event-specific date fields
- `time` - Time fields (HH:MM:SS format)
- `duration` - Duration or time span fields
- `amount` - Monetary amount fields
- `balance` - Balance or outstanding amount fields
- `value` - Market value fields
- `net_flow` - Net flow fields
- `rate` - Rate or percentage change fields
- `ratio` - Structural ratio fields
- `symbol` - Stock symbol fields
- `name` - Name fields
- `code` - Code fields
- `market` - Market identifier fields
- `rank` - Ranking fields
- `count` - Count or quantity fields
- `volume` - Trading volume fields
- `shares` - Share quantity fields
- `boolean` - Boolean flag fields
- `type` - Type or category fields
- `other` - Other field types

## Usage

The FieldMapper class automatically loads all JSON files from this directory when initialized.

```python
from akshare_one.modules.field_naming.field_mapper import FieldMapper

# Initialize with default config directory
mapper = FieldMapper()

# Map fields from source data
df_mapped = mapper.map_fields(df, source='eastmoney', module='fundflow')
```
