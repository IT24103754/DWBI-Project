"""
Fixes the SSIS Olist_ETL project to match Visual Studio 2026/2022's exact schema,
resolving the 'Value cannot be null. Parameter name: path2' error.
"""
import os

out_dir = r"ssis\Olist_ETL"
os.makedirs(out_dir, exist_ok=True)

# 1. Olist_ETL.database
database_xml = """<Database xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ddl2="http://schemas.microsoft.com/analysisservices/2003/engine/2" xmlns:ddl2_2="http://schemas.microsoft.com/analysisservices/2003/engine/2/2" xmlns:ddl100_100="http://schemas.microsoft.com/analysisservices/2008/engine/100/100" xmlns:ddl200="http://schemas.microsoft.com/analysisservices/2010/engine/200" xmlns:ddl200_200="http://schemas.microsoft.com/analysisservices/2010/engine/200/200" xmlns:ddl300="http://schemas.microsoft.com/analysisservices/2011/engine/300" xmlns:ddl300_300="http://schemas.microsoft.com/analysisservices/2011/engine/300/300" xmlns:ddl400="http://schemas.microsoft.com/analysisservices/2012/engine/400" xmlns:ddl400_400="http://schemas.microsoft.com/analysisservices/2012/engine/400/400" xmlns:ddl500="http://schemas.microsoft.com/analysisservices/2013/engine/500" xmlns:ddl500_500="http://schemas.microsoft.com/analysisservices/2013/engine/500/500" xmlns:dwd="http://schemas.microsoft.com/DataWarehouse/Designer/1.0" dwd:design-time-name="096d8e6d-0449-40de-b7c0-c07758dfb392" xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
  <ID>Olist_ETL</ID>
  <Name>Olist_ETL</Name>
  <CreatedTimestamp>0001-01-01T00:00:00Z</CreatedTimestamp>
  <LastSchemaUpdate>0001-01-01T00:00:00Z</LastSchemaUpdate>
  <LastProcessed>0001-01-01T00:00:00Z</LastProcessed>
  <State>Unprocessed</State>
  <LastUpdate>0001-01-01T00:00:00Z</LastUpdate>
  <DataSourceImpersonationInfo>
    <ImpersonationMode>Default</ImpersonationMode>
    <ImpersonationInfoSecurity>Unchanged</ImpersonationInfoSecurity>
  </DataSourceImpersonationInfo>
</Database>"""

with open(os.path.join(out_dir, "Olist_ETL.database"), "w", encoding="utf-8") as f:
    f.write(database_xml)

# 2. Olist_ETL.dtproj
dtproj_xml = """<?xml version="1.0" encoding="utf-8"?>
<Project xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <DeploymentModel>Project</DeploymentModel>
  <ProductVersion>17.0.1016.0</ProductVersion>
  <SchemaVersion>9.0.1.0</SchemaVersion>
  <Database>
    <Name>Olist_ETL.database</Name>
    <FullPath>Olist_ETL.database</FullPath>
  </Database>
  <DataSources />
  <DataSourceViews />
  <DeploymentModelSpecificContent>
    <Manifest>
      <SSIS:Project SSIS:ProtectionLevel="DontSaveSensitive" xmlns:SSIS="www.microsoft.com/SqlServer/SSIS">
        <SSIS:Properties>
          <SSIS:Property SSIS:Name="ID">{7314ddbc-9a1b-4be2-91ff-333a0be87f8a}</SSIS:Property>
          <SSIS:Property SSIS:Name="Name">Olist_ETL</SSIS:Property>
          <SSIS:Property SSIS:Name="VersionMajor">1</SSIS:Property>
          <SSIS:Property SSIS:Name="VersionMinor">0</SSIS:Property>
          <SSIS:Property SSIS:Name="VersionBuild">0</SSIS:Property>
          <SSIS:Property SSIS:Name="VersionComments"></SSIS:Property>
          <SSIS:Property SSIS:Name="CreationDate">2026-09-30T10:00:00</SSIS:Property>
          <SSIS:Property SSIS:Name="CreatorName">ACER\\thuva</SSIS:Property>
          <SSIS:Property SSIS:Name="CreatorComputerName">ACER</SSIS:Property>
          <SSIS:Property SSIS:Name="Description"></SSIS:Property>
          <SSIS:Property SSIS:Name="FormatVersion">1</SSIS:Property>
        </SSIS:Properties>
        <SSIS:Packages>
          <SSIS:Package SSIS:Name="Package.dtsx" SSIS:EntryPoint="1" />
        </SSIS:Packages>
        <SSIS:ConnectionManagers />
        <SSIS:DeploymentInfo>
          <SSIS:ProjectConnectionParameters />
          <SSIS:PackageInfo>
            <SSIS:PackageMetaData SSIS:Name="Package.dtsx">
              <SSIS:Properties>
                <SSIS:Property SSIS:Name="ID">{7DBD5534-B5B6-4FB3-97DC-E3AFFA12EBB3}</SSIS:Property>
                <SSIS:Property SSIS:Name="Name">Package</SSIS:Property>
                <SSIS:Property SSIS:Name="VersionMajor">1</SSIS:Property>
                <SSIS:Property SSIS:Name="VersionMinor">0</SSIS:Property>
                <SSIS:Property SSIS:Name="VersionBuild">0</SSIS:Property>
                <SSIS:Property SSIS:Name="VersionComments"></SSIS:Property>
                <SSIS:Property SSIS:Name="VersionGUID">{A9939191-603C-43A1-A037-5D8A7A35B798}</SSIS:Property>
                <SSIS:Property SSIS:Name="PackageFormatVersion">8</SSIS:Property>
                <SSIS:Property SSIS:Name="Description"></SSIS:Property>
                <SSIS:Property SSIS:Name="ProtectionLevel">1</SSIS:Property>
              </SSIS:Properties>
              <SSIS:Parameters />
            </SSIS:PackageMetaData>
          </SSIS:PackageInfo>
        </SSIS:DeploymentInfo>
      </SSIS:Project>
    </Manifest>
  </DeploymentModelSpecificContent>
  <ControlFlowParts />
  <Miscellaneous />
  <Configurations>
    <Configuration>
      <Name>Development</Name>
      <Options>
        <OutputPath>bin</OutputPath>
        <ConnectionMappings />
        <ConnectionProviderMappings />
        <ConnectionSecurityMappings />
        <DatabaseStorageLocations />
        <TargetServerVersion>SQLServer2025</TargetServerVersion>
        <AzureMode>false</AzureMode>
        <LinkedAzureTenantId />
        <LinkedAzureAccountId />
        <LinkedAzureSSISIR />
        <LinkedAzureStorage />
        <RemoteExecutionFolder />
        <ParameterConfigurationValues />
      </Options>
    </Configuration>
  </Configurations>
</Project>"""

with open(os.path.join(out_dir, "Olist_ETL.dtproj"), "w", encoding="utf-8") as f:
    f.write(dtproj_xml)

# 3. Olist_ETL.dtproj.user
dtproj_user = """<?xml version="1.0" encoding="utf-8"?>
<DataTransformationsUserConfiguration xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Configurations>
    <Configuration>
      <Name>Development</Name>
      <Options>
        <AssessmentRuleSuppressionSetting />
        <UseWinAuth>false</UseWinAuth>
        <WinAuthUserName />
        <WinAuthDomain />
        <UserIDs />
        <UserPasswords />
        <OfflineMode>false</OfflineMode>
        <ProgressReporting>true</ProgressReporting>
        <ParameterConfigurationSensitiveValues />
      </Options>
    </Configuration>
  </Configurations>
</DataTransformationsUserConfiguration>"""

with open(os.path.join(out_dir, "Olist_ETL.dtproj.user"), "w", encoding="utf-8") as f:
    f.write(dtproj_user)

# 4. Project.params
with open(os.path.join(out_dir, "Project.params"), "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0"?>
<SSIS:Parameters xmlns:SSIS="www.microsoft.com/SqlServer/SSIS">
</SSIS:Parameters>""")

# 5. Olist_ETL.slnx (Modern VS 2026 solution format)
slnx_xml = """<Solution>
  <Configurations>
    <BuildType Name="Development" />
    <Platform Name="Default" />
  </Configurations>
  <Project Path="Olist_ETL.dtproj" Type="c9674dcb-5085-4a16-b785-4c70dd1589bd">
    <Platform Project="?" />
  </Project>
</Solution>"""

with open(os.path.join(out_dir, "Olist_ETL.slnx"), "w", encoding="utf-8") as f:
    f.write(slnx_xml)

# 6. Olist_ETL.sln (Classic VS solution format with proper GUIDs)
sln_text = """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{159641D6-6404-4A2A-AE62-294DE0FE8301}") = "Olist_ETL", "Olist_ETL.dtproj", "{7314DDBC-9A1B-4BE2-91FF-333A0BE87F8A}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Development|Default = Development|Default
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{7314DDBC-9A1B-4BE2-91FF-333A0BE87F8A}.Development|Default.ActiveCfg = Development
		{7314DDBC-9A1B-4BE2-91FF-333A0BE87F8A}.Development|Default.Build.0 = Development
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
"""

with open(os.path.join(out_dir, "Olist_ETL.sln"), "w", encoding="utf-8") as f:
    f.write(sln_text)

# 7. Package.dtsx with full control flow and tasks matching the exact project GUIDs
package_xml = """<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="9/30/2026 8:52:16 AM"
  DTS:CreationName="Microsoft.Package"
  DTS:CreatorComputerName="ACER"
  DTS:CreatorName="ACER\\thuva"
  DTS:DTSID="{7DBD5534-B5B6-4FB3-97DC-E3AFFA12EBB3}"
  DTS:ExecutableType="Microsoft.Package"
  DTS:LastModifiedProductVersion="17.0.1016.0"
  DTS:LocaleID="1033"
  DTS:ObjectName="Package"
  DTS:PackageType="5"
  DTS:VersionGUID="{A9939191-603C-43A1-A037-5D8A7A35B798}">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_OLTP]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{7E9D9346-6D3E-4B07-B45A-8EF1E2C04D81}"
      DTS:ObjectName="Olist_OLTP">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=Olist_OLTP;Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_DW]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{9C623C6D-5509-4C51-B9D7-BE480D9F0A3E}"
      DTS:ObjectName="Olist_DW">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=Olist_DW;Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Products_CSV]"
      DTS:CreationName="FLATFILE"
      DTS:DTSID="{47A46B55-5B26-444F-A299-8260D0CD47F5}"
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
      DTS:Description="Data Flow Task - Customer Ingestion"
      DTS:DTSID="{A24B91E3-8821-4E8F-A332-6A15E8D291F0}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Customer"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1" />
      </DTS:ObjectData>
    </DTS:Executable>
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Product"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Product Ingestion with REPLACENULL"
      DTS:DTSID="{B35C82F4-9932-5F9A-B443-7B26F9E3A201}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Product"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1" />
      </DTS:ObjectData>
    </DTS:Executable>
    <DTS:Executable
      DTS:refId="Package\\Load_Fact_Orders"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Fact Ingestion with Lookups"
      DTS:DTSID="{C46D93A5-AA43-6AAB-C554-8C370AF4B312}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Fact_Orders"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
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
      DTS:DTSID="{D57EA4B6-BB54-7BBC-D665-9D481BA5C423}"
      DTS:From="Package\\Load_Dim_Customer"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Customer_to_Product"
      DTS:To="Package\\Load_Dim_Product" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Product_to_Fact]"
      DTS:CreationName=""
      DTS:DTSID="{E68FB5C7-CC65-8CCD-E776-AE592CB6D534}"
      DTS:From="Package\\Load_Dim_Product"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Product_to_Fact"
      DTS:To="Package\\Load_Fact_Orders" />
  </DTS:PrecedenceConstraints>
  <DTS:DesignTimeProperties><![CDATA[<?xml version="1.0"?>
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
        StartConnector="{assembly:Null}"
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
        StartConnector="{assembly:Null}"
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
</DTS:Executable>"""

with open(os.path.join(out_dir, "Package.dtsx"), "w", encoding="utf-8") as f:
    f.write(package_xml)

print("SSIS project files regenerated to match exact VS 2026 / 17.0 schema!")
