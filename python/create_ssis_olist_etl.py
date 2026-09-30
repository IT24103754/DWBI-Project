import os, uuid

def get_guid():
    return '{' + str(uuid.uuid4()).upper() + '}'

pkg_id = get_guid()
conn_oltp_id = get_guid()
conn_dw_id = get_guid()
conn_csv_id = get_guid()
task1_id = get_guid()
task2_id = get_guid()
task3_id = get_guid()
pc1_id = get_guid()
pc2_id = get_guid()

dtsx_content = f'''<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="2026-09-30T10:00:00Z"
  DTS:CreatorName="Antigravity"
  DTS:DTSID="{pkg_id}"
  DTS:ExecutableType="Microsoft.Package"
  DTS:LastModifiedProductVersion="16.0.5035.3"
  DTS:LocaleID="1033"
  DTS:ObjectName="Package"
  DTS:PackageType="5"
  DTS:VersionBuild="1"
  DTS:VersionGUID="{get_guid()}">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_OLTP]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{conn_oltp_id}"
      DTS:ObjectName="Olist_OLTP">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=OlistDW;Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_DW]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{conn_dw_id}"
      DTS:ObjectName="Olist_DW">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=OlistDW;Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Products_CSV]"
      DTS:CreationName="FLATFILE"
      DTS:DTSID="{conn_csv_id}"
      DTS:ObjectName="Products_CSV">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:Format="Delimited"
          DTS:LocaleID="1033"
          DTS:HeaderRowDelimiter="_x000D__x000A_"
          DTS:ColumnNamesInFirstDataRow="True"
          DTS:RowDelimiter=""
          DTS:ConnectionString="c:\\Users\\thuva\\OneDrive\\Desktop\\DWBI Project\\Dataset\\olist_products_dataset.csv">
        </DTS:ConnectionManager>
      </DTS:ObjectData>
    </DTS:ConnectionManager>
  </DTS:ConnectionManagers>
  <DTS:Variables />
  <DTS:Executables>
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Customer"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Extracts Customers from Source and populates Dim_Customer with surrogate identity keys"
      DTS:DTSID="{task1_id}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Customer"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;http://www.microsoft.com/sql/support/default.asp;1">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1" />
      </DTS:ObjectData>
    </DTS:Executable>
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Product"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Extracts Products CSV, applies Derived Column REPLACENULL transformation for missing values, and loads Dim_Product"
      DTS:DTSID="{task2_id}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Product"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;http://www.microsoft.com/sql/support/default.asp;1">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1" />
      </DTS:ObjectData>
    </DTS:Executable>
    <DTS:Executable
      DTS:refId="Package\\Load_Fact_Orders"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Extracts delivered orders via SQL query, performs sequential Lookups on Customer, Product, and Seller with Ignore Failure, and loads Fact_Orders"
      DTS:DTSID="{task3_id}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Fact_Orders"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;http://www.microsoft.com/sql/support/default.asp;1">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1" />
      </DTS:ObjectData>
    </DTS:Executable>
  </DTS:Executables>
  <DTS:PrecedenceConstraints>
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Customer_to_Product]"
      DTS:CreationName=""
      DTS:DTSID="{pc1_id}"
      DTS:From="Package\\Load_Dim_Customer"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Customer_to_Product"
      DTS:To="Package\\Load_Dim_Product" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Product_to_Fact]"
      DTS:CreationName=""
      DTS:DTSID="{pc2_id}"
      DTS:From="Package\\Load_Dim_Product"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Product_to_Fact"
      DTS:To="Package\\Load_Fact_Orders" />
  </DTS:PrecedenceConstraints>
  <DTS:DesignTimeProperties><![CDATA[<?xml version="1.0"?>
<!--Package layout information-->
<GraphLayout xmlns="clr-namespace:Microsoft.SqlServer.IntegrationServices.Designer.Model.Serialization;assembly=Microsoft.SqlServer.IntegrationServices.Graph" xmlns:mssgle="clr-namespace:Microsoft.SqlServer.Graph.LayoutEngine;assembly=Microsoft.SqlServer.Graph" xmlns:assembly="http://schemas.microsoft.com/winfx/2006/xaml">
  <NodeLayout
    Size="195,42"
    Id="Package\\Load_Dim_Customer"
    TopLeft="120,50" />
  <NodeLayout
    Size="185,42"
    Id="Package\\Load_Dim_Product"
    TopLeft="125,140" />
  <NodeLayout
    Size="180,42"
    Id="Package\\Load_Fact_Orders"
    TopLeft="128,230" />
  <EdgeLayout
    Id="Package.PrecedenceConstraints[Constraint_Customer_to_Product]"
    TopLeft="217.5,92">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{{assembly:Null}}"
        EndConnector="0,48"
        Start="0,0"
        End="0,40.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,40.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
  <EdgeLayout
    Id="Package.PrecedenceConstraints[Constraint_Product_to_Fact]"
    TopLeft="217.5,182">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{{assembly:Null}}"
        EndConnector="0,48"
        Start="0,0"
        End="0,40.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,40.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
</GraphLayout>
]]></DTS:DesignTimeProperties>
</DTS:Executable>
'''

out_dir = r'ssis\Olist_ETL'
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'Package.dtsx'), 'w', encoding='utf-8') as f:
    f.write(dtsx_content)

dtproj_content = '''<?xml version="1.0" encoding="utf-8"?>
<Project xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <ProductVersion>16.0.5035.3</ProductVersion>
  <SchemaVersion>9.0</SchemaVersion>
  <Database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <Name>Olist_ETL</Name>
    <Packages>
      <Package>
        <Name>Package.dtsx</Name>
        <FullPath>Package.dtsx</FullPath>
      </Package>
    </Packages>
    <ConnectionManagers>
      <ConnectionManager>
        <Name>Olist_OLTP.conmgr</Name>
        <FullPath>Olist_OLTP.conmgr</FullPath>
      </ConnectionManager>
      <ConnectionManager>
        <Name>Olist_DW.conmgr</Name>
        <FullPath>Olist_DW.conmgr</FullPath>
      </ConnectionManager>
      <ConnectionManager>
        <Name>Products_CSV.conmgr</Name>
        <FullPath>Products_CSV.conmgr</FullPath>
      </ConnectionManager>
    </ConnectionManagers>
  </Database>
</Project>
'''
with open(os.path.join(out_dir, 'Olist_ETL.dtproj'), 'w', encoding='utf-8') as f:
    f.write(dtproj_content)

sln_content = '''Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{159641D6-6404-4A2A-AE62-294DE0FE8301}") = "Olist_ETL", "Olist_ETL.dtproj", "{A1E6B93F-11B4-4D2A-93B2-5FA995DFE825}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Development|Default = Development|Default
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{A1E6B93F-11B4-4D2A-93B2-5FA995DFE825}.Development|Default.ActiveCfg = Development
		{A1E6B93F-11B4-4D2A-93B2-5FA995DFE825}.Development|Default.Build.0 = Development
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
'''
with open(os.path.join(out_dir, 'Olist_ETL.sln'), 'w', encoding='utf-8') as f:
    f.write(sln_content)

print('SSIS Olist_ETL project created successfully!')
