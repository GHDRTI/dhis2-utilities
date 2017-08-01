require 'csv'
require 'optparse'
require 'json'



options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: import-orgs.rb -i orgs.csv"
  opts.on('-i', '--input filename', 'Input CSV file') { |v| 
    options[:input] = v 
  }
end.parse!

if options[:input].nil? || options[:input].empty?
  puts "Input CSV required"
  exit
end

parentid = "tsCcDA5DiQh"

def to_element orgname, orgcode
  
  parent = {
    "id": parentid
  }

  element = {
    'name' => orgname,
    'code' => orgcode,
    'shortName' => orgname,
    "openingDate" => "2010-08-01T00:00:00.000",
    "parent" => parent
  }

  return element
end

#puts options[:input]
orgunits = []

CSV.foreach(options[:input]) do |row|
  orgunits.push(to_element(row[0], row[1]))
end


export = {:organisationUnits => orgunits}

puts JSON.generate(export)

