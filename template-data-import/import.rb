require 'roo'
require 'roo-xls'
require 'optparse'
require 'json'

def open_workbook filename
  begin
    Roo::Spreadsheet.open(filename, extension: :xlsx)
  rescue Zip::Error
    Roo::Spreadsheet.open(filename)
  end
end

def get_orgs sheet
  org_unit_id_col = 'B'
  org_unit_ids = {}
  row = 6
  blank_count = 0
  while blank_count < 3 do
    id = sheet.cell org_unit_id_col, row
    if !id.nil? && !id.empty?
      org_unit_ids[row] = id
      blank_count = 0
    else
      blank_count += 1
    end
    row += 1
  end
  return org_unit_ids
end

def to_element sheet, row, column, org_unit_id
  element = {
    'orgUnit' => org_unit_id,
    'dataElement' => sheet.cell(2, 3),
    'value' => sheet.cell(row, column),
    'period' => sheet.cell(5, column).to_s,
    'followUp' => false
  }
  cat = sheet.cell(4, column) 
  element['categoryOptionCombo'] = cat unless cat.nil? || (cat.is_a?(String) && cat.empty?)
  
  attribute = sheet.cell(2, 8)
  element['attrOptionCombo'] = attribute unless attribute.nil? || (attribute.is_a?(String) && attribute.empty?)

  return element
end


options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: import.rb [options]"
  opts.on('-w', '--workbook filename', 'Source workbook file') { |v| 
    options[:workbook] = v 
  }
  opts.on('-o', '--output filename', 'Output JSON file') { |v| 
    options[:output] = v 
  }
end.parse!

if options[:output].nil? || options[:output].empty?
  puts "Output file required"
  exit
end

workbook = open_workbook options[:workbook]
data_values = []

workbook.sheets.each do |sheet_name|

  sheet = workbook.sheet sheet_name
  org_unit_ids = get_orgs sheet

  column = 3
  while column <= sheet.last_column
    org_unit_ids.each do |row, org_unit_id|
      val = sheet.cell(row, column)
      unless val.nil? || (val.is_a?(String) && val.empty?)
        data_values << to_element(sheet, row, column, org_unit_id)
      end
    end
    column += 1
  end

end

File.write(options[:output], JSON.generate({"dataValues" => data_values}))