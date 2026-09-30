"""
build_all_dimensions_package.py
Generates an all-inclusive SSIS Package with 5 tasks in Control Flow:
1. Load_Dim_Customer  (Data Flow Task: OLE DB Source -> Destination)
2. Load_Dim_Product   (Data Flow Task: OLE DB Source with REPLACENULL -> Destination)
3. Load_Dim_Seller    (Data Flow Task: OLE DB Source -> Destination)
4. Load_Dim_Date      (Execute SQL Task: Dim_Date Generator)
5. Load_Fact_Orders   (Data Flow Task: Fact Orders with Lookups -> Destination)
"""

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
  DTS:ProtectionLevel="0"
  DTS:DelayValidation="True"
  DTS:VersionBuild="10"
  DTS:VersionGUID="{7A19D3B2-824F-4C2E-AA51-9C8E32D4B5E6}">
  <DTS:Property
    DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_DW]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{9C623C6D-5509-4C51-B9D7-BE480D9F0A3E}"
      DTS:ObjectName="Olist_DW">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectRetryCount="1"
          DTS:ConnectRetryInterval="5"
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=Olist_DW;Provider=MSOLEDBSQL;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_OLTP]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{7E9D9346-6D3E-4B07-B45A-8EF1E2C04D81}"
      DTS:ObjectName="Olist_OLTP">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectRetryCount="1"
          DTS:ConnectRetryInterval="5"
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=Olist_OLTP;Provider=MSOLEDBSQL;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
  </DTS:ConnectionManagers>
  <DTS:Variables />
  <DTS:Executables>
    <!-- Task 0: Prepare_DW_Tables -->
    <DTS:Executable
      DTS:refId="Package\\Prepare_DW_Tables"
      DTS:CreationName="Microsoft.ExecuteSQLTask"
      DTS:DelayValidation="True"
      DTS:Description="Cleans and resets Fact and Dimension tables for idempotent full refresh"
      DTS:DTSID="{A1B2C3D4-E5F6-4A1B-8C2D-3E4F5A6B7C8D}"
      DTS:ExecutableType="Microsoft.ExecuteSQLTask"
      DTS:LocaleID="-1"
      DTS:ObjectName="Prepare_DW_Tables"
      DTS:TaskContact="Execute SQL Task; Microsoft Corporation; SQL Server 2025; © 2025 Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <SQLTask:SqlTaskData
          SQLTask:Connection="{9C623C6D-5509-4C51-B9D7-BE480D9F0A3E}"
          SQLTask:SqlStatementSource="TRUNCATE TABLE dbo.Fact_Orders;&#xA;DELETE FROM dbo.Dim_Customer; DBCC CHECKIDENT ('dbo.Dim_Customer', RESEED, 0);&#xA;DELETE FROM dbo.Dim_Product; DBCC CHECKIDENT ('dbo.Dim_Product', RESEED, 0);&#xA;DELETE FROM dbo.Dim_Seller; DBCC CHECKIDENT ('dbo.Dim_Seller', RESEED, 0);" xmlns:SQLTask="www.microsoft.com/sqlserver/dts/tasks/sqltask" />
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- Task 1: Load_Dim_Customer -->
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Customer"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:DelayValidation="True"
      DTS:Description="Data Flow Task - Extracts Customers from Olist_OLTP and loads Dim_Customer"
      DTS:DTSID="{A24B91E3-8821-4E8F-A332-6A15E8D291F0}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Customer"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline
          version="1">
          <components>
            <component
              refId="Package\\Load_Dim_Customer\\OLE DB Source"
              componentClassID="Microsoft.OLEDBSource"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Extracts customer master data from Olist_OLTP"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset">[dbo].[olist_customers_dataset]</property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor">SELECT customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state FROM dbo.olist_customers_dataset</property>
                <property dataType="System.String" description="The variable that contains the SQL command to be executed." name="SqlCommandVariable"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">2</property>
                <property dataType="System.String" description="The mappings between the parameters in the SQL command and variables." name="ParameterMapping"></property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Customer\\OLE DB Source.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_OLTP]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_OLTP]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output]"
                  name="OLE DB Source Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_id]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_id]"
                      length="50"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_id]"
                      name="customer_id"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_unique_id]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_unique_id]"
                      length="50"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_unique_id]"
                      name="customer_unique_id"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_zip_code_prefix]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_zip_code_prefix]"
                      length="10"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_zip_code_prefix]"
                      name="customer_zip_code_prefix"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_city]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_city]"
                      length="100"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_city]"
                      name="customer_city"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_state]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_state]"
                      length="5"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_state]"
                      name="customer_state"
                      truncationRowDisposition="FailComponent" />
                  </outputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      name="customer_id" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_unique_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      name="customer_unique_id" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_zip_code_prefix]"
                      codePage="1252"
                      dataType="str"
                      length="10"
                      name="customer_zip_code_prefix" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_city]"
                      codePage="1252"
                      dataType="str"
                      length="100"
                      name="customer_city" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[customer_state]"
                      codePage="1252"
                      dataType="str"
                      length="5"
                      name="customer_state" />
                  </externalMetadataColumns>
                </output>
                <output
                  refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output]"
                  isErrorOut="true"
                  name="OLE DB Source Error Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_id]"
                      name="customer_id" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_unique_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_unique_id]"
                      name="customer_unique_id" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_zip_code_prefix]"
                      codePage="1252"
                      dataType="str"
                      length="10"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_zip_code_prefix]"
                      name="customer_zip_code_prefix" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_city]"
                      codePage="1252"
                      dataType="str"
                      length="100"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_city]"
                      name="customer_city" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_state]"
                      codePage="1252"
                      dataType="str"
                      length="5"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[customer_state]"
                      name="customer_state" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Dim_Customer\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Loads customer dimensions into Olist_DW"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset">[dbo].[Dim_Customer]</property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="Indicates whether the values supplied for identity columns will be copied to the destination." name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="Indicates whether the columns containing null will have null inserted in the destination." name="FastLoadKeepNulls">false</property>
                <property dataType="System.String" description="Specifies options to be used with fast load." name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
                <property dataType="System.Int32" description="Specifies when commits are issued during data insertion." name="FastLoadMaxInsertCommitSize">2147483647</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Customer\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <inputColumns>
                    <inputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[customer_id]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="50"
                      cachedName="customer_id"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerBK]"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_id]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[customer_unique_id]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="50"
                      cachedName="customer_unique_id"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerUniqueId]"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_unique_id]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[customer_zip_code_prefix]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="10"
                      cachedName="customer_zip_code_prefix"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerZipCode]"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_zip_code_prefix]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[customer_city]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="100"
                      cachedName="customer_city"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerCity]"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_city]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[customer_state]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="5"
                      cachedName="customer_state"
                      externalMetadataColumnId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerState]"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output].Columns[customer_state]" />
                  </inputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerBK]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="CustomerBK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerUniqueId]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="CustomerUniqueId" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerZipCode]"
                      codePage="1252"
                      dataType="str"
                      length="16"
                      name="CustomerZipCode" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerCity]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="CustomerCity" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerState]"
                      codePage="1252"
                      dataType="str"
                      length="16"
                      name="CustomerState" />
                  </externalMetadataColumns>
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Customer\\OLE DB Destination.Outputs[OLE DB Destination Error Output]"
                  exclusionGroup="1"
                  isErrorOut="true"
                  name="OLE DB Destination Error Output"
                  synchronousInputId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input]">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Dim_Customer\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Customer\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Dim_Customer.Paths[OLE DB Source Output]"
              endId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="OLE DB Source Output"
              startId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- Task 2: Load_Dim_Product -->
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Product"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:DelayValidation="True"
      DTS:Description="Data Flow Task - Extracts Products from Olist_OLTP, applies REPLACENULL, loads Dim_Product"
      DTS:DTSID="{B35C82F4-9932-5F9A-B443-7B26F9E3A201}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Product"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline
          version="1">
          <components>
            <component
              refId="Package\\Load_Dim_Product\\OLE DB Source"
              componentClassID="Microsoft.OLEDBSource"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Extracts products dataset from Olist_OLTP"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset"></property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor">SELECT product_id, ISNULL(NULLIF(LTRIM(RTRIM(product_category_name)), ''), 'Unknown') AS product_category_name, product_weight_g, product_length_cm, product_height_cm, product_width_cm FROM dbo.olist_products_dataset</property>
                <property dataType="System.String" description="The variable that contains the SQL command to be executed." name="SqlCommandVariable"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">2</property>
                <property dataType="System.String" description="The mappings between the parameters in the SQL command and variables." name="ParameterMapping"></property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Product\\OLE DB Source.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_OLTP]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_OLTP]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output]"
                  name="OLE DB Source Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_id]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_id]"
                      length="50"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_id]"
                      name="product_id"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_category_name]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_category_name]"
                      length="100"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_category_name]"
                      name="product_category_name"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_weight_g]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_weight_g]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_weight_g]"
                      name="product_weight_g"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_length_cm]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_length_cm]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_length_cm]"
                      name="product_length_cm"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_height_cm]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_height_cm]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_height_cm]"
                      name="product_height_cm"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_width_cm]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_width_cm]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_width_cm]"
                      name="product_width_cm"
                      truncationRowDisposition="FailComponent" />
                  </outputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      name="product_id" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_category_name]"
                      codePage="1252"
                      dataType="str"
                      length="100"
                      name="product_category_name" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_weight_g]"
                      dataType="i4"
                      name="product_weight_g" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_length_cm]"
                      dataType="i4"
                      name="product_length_cm" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_height_cm]"
                      dataType="i4"
                      name="product_height_cm" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[product_width_cm]"
                      dataType="i4"
                      name="product_width_cm" />
                  </externalMetadataColumns>
                </output>
                <output
                  refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output]"
                  isErrorOut="true"
                  name="OLE DB Source Error Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_id]"
                      name="product_id" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_category_name]"
                      codePage="1252"
                      dataType="str"
                      length="100"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_category_name]"
                      name="product_category_name" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_weight_g]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_weight_g]"
                      name="product_weight_g" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_length_cm]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_length_cm]"
                      name="product_length_cm" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_height_cm]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_height_cm]"
                      name="product_height_cm" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_width_cm]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[product_width_cm]"
                      name="product_width_cm" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Dim_Product\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Loads clean product dimensions into Olist_DW"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset">[dbo].[Dim_Product]</property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="Indicates whether the values supplied for identity columns will be copied to the destination." name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="Indicates whether the columns containing null will have null inserted in the destination." name="FastLoadKeepNulls">false</property>
                <property dataType="System.String" description="Specifies options to be used with fast load." name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
                <property dataType="System.Int32" description="Specifies when commits are issued during data insertion." name="FastLoadMaxInsertCommitSize">2147483647</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Product\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <inputColumns>
                    <inputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[product_id]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="50"
                      cachedName="product_id"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductBK]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_id]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[product_category_name]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="100"
                      cachedName="product_category_name"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CategoryNameEnglish]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_category_name]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[product_weight_g]"
                      cachedDataType="i4"
                      cachedName="product_weight_g"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductWeightGrams]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_weight_g]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[product_length_cm]"
                      cachedDataType="i4"
                      cachedName="product_length_cm"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductLengthCm]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_length_cm]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[product_height_cm]"
                      cachedDataType="i4"
                      cachedName="product_height_cm"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductHeightCm]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_height_cm]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[product_width_cm]"
                      cachedDataType="i4"
                      cachedName="product_width_cm"
                      externalMetadataColumnId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductWidthCm]"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output].Columns[product_width_cm]" />
                  </inputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductBK]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="ProductBK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CategoryNameEnglish]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="CategoryNameEnglish" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductWeightGrams]"
                      dataType="i4"
                      name="ProductWeightGrams" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductLengthCm]"
                      dataType="i4"
                      name="ProductLengthCm" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductHeightCm]"
                      dataType="i4"
                      name="ProductHeightCm" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductWidthCm]"
                      dataType="i4"
                      name="ProductWidthCm" />
                  </externalMetadataColumns>
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Product\\OLE DB Destination.Outputs[OLE DB Destination Error Output]"
                  exclusionGroup="1"
                  isErrorOut="true"
                  name="OLE DB Destination Error Output"
                  synchronousInputId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input]">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Dim_Product\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Product\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Dim_Product.Paths[OLE DB Source Output]"
              endId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="OLE DB Source Output"
              startId="Package\\Load_Dim_Product\\OLE DB Source.Outputs[OLE DB Source Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- Task 3: Load_Dim_Seller -->
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Seller"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:DelayValidation="True"
      DTS:Description="Data Flow Task - Extracts Sellers from Olist_OLTP and loads Dim_Seller"
      DTS:DTSID="{E53A81F2-7214-4B29-87DA-92F67104BE21}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Seller"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline
          version="1">
          <components>
            <component
              refId="Package\\Load_Dim_Seller\\OLE DB Source"
              componentClassID="Microsoft.OLEDBSource"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Extracts sellers dataset from Olist_OLTP"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset">[dbo].[olist_sellers_dataset]</property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor">SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state FROM dbo.olist_sellers_dataset</property>
                <property dataType="System.String" description="The variable that contains the SQL command to be executed." name="SqlCommandVariable"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">2</property>
                <property dataType="System.String" description="The mappings between the parameters in the SQL command and variables." name="ParameterMapping"></property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Seller\\OLE DB Source.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_OLTP]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_OLTP]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output]"
                  name="OLE DB Source Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_id]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_id]"
                      length="50"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_id]"
                      name="seller_id"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_zip_code_prefix]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_zip_code_prefix]"
                      length="10"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_zip_code_prefix]"
                      name="seller_zip_code_prefix"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_city]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_city]"
                      length="100"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_city]"
                      name="seller_city"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_state]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_state]"
                      length="5"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_state]"
                      name="seller_state"
                      truncationRowDisposition="FailComponent" />
                  </outputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      name="seller_id" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_zip_code_prefix]"
                      codePage="1252"
                      dataType="str"
                      length="10"
                      name="seller_zip_code_prefix" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_city]"
                      codePage="1252"
                      dataType="str"
                      length="100"
                      name="seller_city" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[seller_state]"
                      codePage="1252"
                      dataType="str"
                      length="5"
                      name="seller_state" />
                  </externalMetadataColumns>
                </output>
                <output
                  refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output]"
                  isErrorOut="true"
                  name="OLE DB Source Error Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_id]"
                      name="seller_id" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_zip_code_prefix]"
                      codePage="1252"
                      dataType="str"
                      length="10"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_zip_code_prefix]"
                      name="seller_zip_code_prefix" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_city]"
                      codePage="1252"
                      dataType="str"
                      length="100"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_city]"
                      name="seller_city" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_state]"
                      codePage="1252"
                      dataType="str"
                      length="5"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[seller_state]"
                      name="seller_state" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Dim_Seller\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Loads merchant dimensions into Olist_DW"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset">[dbo].[Dim_Seller]</property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="Indicates whether the values supplied for identity columns will be copied to the destination." name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="Indicates whether the columns containing null will have null inserted in the destination." name="FastLoadKeepNulls">false</property>
                <property dataType="System.String" description="Specifies options to be used with fast load." name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
                <property dataType="System.Int32" description="Specifies when commits are issued during data insertion." name="FastLoadMaxInsertCommitSize">2147483647</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Seller\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <inputColumns>
                    <inputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[seller_id]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="50"
                      cachedName="seller_id"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerBK]"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_id]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[seller_zip_code_prefix]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="10"
                      cachedName="seller_zip_code_prefix"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerZipCode]"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_zip_code_prefix]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[seller_city]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="100"
                      cachedName="seller_city"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerCity]"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_city]" />
                    <inputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[seller_state]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="5"
                      cachedName="seller_state"
                      externalMetadataColumnId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerState]"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output].Columns[seller_state]" />
                  </inputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerBK]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="SellerBK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerZipCode]"
                      codePage="1252"
                      dataType="str"
                      length="16"
                      name="SellerZipCode" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerCity]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="SellerCity" />
                    <externalMetadataColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerState]"
                      codePage="1252"
                      dataType="str"
                      length="16"
                      name="SellerState" />
                  </externalMetadataColumns>
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Seller\\OLE DB Destination.Outputs[OLE DB Destination Error Output]"
                  exclusionGroup="1"
                  isErrorOut="true"
                  name="OLE DB Destination Error Output"
                  synchronousInputId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input]">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Dim_Seller\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Dim_Seller\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Dim_Seller.Paths[OLE DB Source Output]"
              endId="Package\\Load_Dim_Seller\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="OLE DB Source Output"
              startId="Package\\Load_Dim_Seller\\OLE DB Source.Outputs[OLE DB Source Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- Task 4: Load_Dim_Date -->
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Date"
      DTS:CreationName="Microsoft.ExecuteSQLTask"
      DTS:DelayValidation="True"
      DTS:Description="Generates calendar dimension dates in Olist_DW"
      DTS:DTSID="{D487291B-8234-4C78-98AA-8B12C3456789}"
      DTS:ExecutableType="Microsoft.ExecuteSQLTask"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Date"
      DTS:TaskContact="Execute SQL Task; Microsoft Corporation; SQL Server 2025; © 2025 Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <SQLTask:SqlTaskData
          SQLTask:Connection="{9C623C6D-5509-4C51-B9D7-BE480D9F0A3E}"
          SQLTask:SqlStatementSource="IF NOT EXISTS (SELECT 1 FROM dbo.Dim_Date)&#xA;BEGIN&#xA;    DECLARE @StartDate DATE = '2016-01-01', @EndDate DATE = '2019-12-31';&#xA;    WITH DateRange AS (&#xA;        SELECT @StartDate AS [Date]&#xA;        UNION ALL&#xA;        SELECT DATEADD(day, 1, [Date]) FROM DateRange WHERE [Date] &lt; @EndDate&#xA;    )&#xA;    INSERT INTO dbo.Dim_Date (DateKey, FullDate, [Day], [Month], MonthName, [Quarter], [Year], DayOfWeekName, IsWeekend)&#xA;    SELECT &#xA;        CAST(CONVERT(VARCHAR(8), [Date], 112) AS INT),&#xA;        [Date], DAY([Date]), MONTH([Date]), DATENAME(month, [Date]),&#xA;        DATEPART(quarter, [Date]), YEAR([Date]), DATENAME(weekday, [Date]),&#xA;        CASE WHEN DATEPART(weekday, [Date]) IN (1, 7) THEN 1 ELSE 0 END&#xA;    FROM DateRange OPTION (MAXRECURSION 3000);&#xA;END" xmlns:SQLTask="www.microsoft.com/sqlserver/dts/tasks/sqltask" />
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- Task 5: Load_Fact_Orders -->
    <DTS:Executable
      DTS:refId="Package\\Load_Fact_Orders"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:DelayValidation="True"
      DTS:Description="Extracts delivered transactions from Olist_OLTP with Lookups, loads Fact_Orders"
      DTS:DTSID="{C46D93A5-AA43-6AAB-C554-8C370AF4B312}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Fact_Orders"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline
          version="1">
          <components>
            <component
              refId="Package\\Load_Fact_Orders\\OLE DB Source"
              componentClassID="Microsoft.OLEDBSource"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Extracts delivered order transactions from Olist_OLTP with resolved keys"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset"></property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor">SELECT oi.order_id, oi.order_item_id, c.CustomerSK, p.ProductSK, s.SellerSK, CAST(CONVERT(VARCHAR(8), o.order_purchase_timestamp, 112) AS INT) AS DateKey, oi.price, oi.freight_value, CAST((oi.price + oi.freight_value) AS DECIMAL(18,2)) AS TotalOrderValue, DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS DeliveryTimeDays FROM Olist_OLTP.dbo.olist_orders_dataset o INNER JOIN Olist_OLTP.dbo.olist_order_items_dataset oi ON o.order_id = oi.order_id INNER JOIN Olist_DW.dbo.Dim_Customer c ON o.customer_id = c.CustomerBK INNER JOIN Olist_DW.dbo.Dim_Product p ON oi.product_id = p.ProductBK LEFT JOIN Olist_DW.dbo.Dim_Seller s ON oi.seller_id = s.SellerBK WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL</property>
                <property dataType="System.String" description="The variable that contains the SQL command to be executed." name="SqlCommandVariable"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">2</property>
                <property dataType="System.String" description="The mappings between the parameters in the SQL command and variables." name="ParameterMapping"></property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\OLE DB Source.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_OLTP]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_OLTP]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output]"
                  name="OLE DB Source Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[order_id]"
                      codePage="1252"
                      dataType="str"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[order_id]"
                      length="50"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[order_id]"
                      name="order_id"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[order_item_id]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[order_item_id]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[order_item_id]"
                      name="order_item_id"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[CustomerSK]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[CustomerSK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[CustomerSK]"
                      name="CustomerSK"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[ProductSK]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[ProductSK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[ProductSK]"
                      name="ProductSK"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[SellerSK]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[SellerSK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[SellerSK]"
                      name="SellerSK"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[DateKey]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[DateKey]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[DateKey]"
                      name="DateKey"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[price]"
                      dataType="numeric"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[price]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[price]"
                      name="price"
                      precision="18"
                      scale="2"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[freight_value]"
                      dataType="numeric"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[freight_value]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[freight_value]"
                      name="freight_value"
                      precision="18"
                      scale="2"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[TotalOrderValue]"
                      dataType="numeric"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[TotalOrderValue]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[TotalOrderValue]"
                      name="TotalOrderValue"
                      precision="18"
                      scale="2"
                      truncationRowDisposition="FailComponent" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[DeliveryTimeDays]"
                      dataType="i4"
                      errorOrTruncationOperation="Conversion"
                      errorRowDisposition="FailComponent"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[DeliveryTimeDays]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[DeliveryTimeDays]"
                      name="DeliveryTimeDays"
                      truncationRowDisposition="FailComponent" />
                  </outputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[order_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      name="order_id" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[order_item_id]"
                      dataType="i4"
                      name="order_item_id" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[CustomerSK]"
                      dataType="i4"
                      name="CustomerSK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[ProductSK]"
                      dataType="i4"
                      name="ProductSK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[SellerSK]"
                      dataType="i4"
                      name="SellerSK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[DateKey]"
                      dataType="i4"
                      name="DateKey" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[price]"
                      dataType="numeric"
                      name="price"
                      precision="18"
                      scale="2" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[freight_value]"
                      dataType="numeric"
                      name="freight_value"
                      precision="18"
                      scale="2" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[TotalOrderValue]"
                      dataType="numeric"
                      name="TotalOrderValue"
                      precision="18"
                      scale="2" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].ExternalColumns[DeliveryTimeDays]"
                      dataType="i4"
                      name="DeliveryTimeDays" />
                  </externalMetadataColumns>
                </output>
                <output
                  refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output]"
                  isErrorOut="true"
                  name="OLE DB Source Error Output">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[order_id]"
                      codePage="1252"
                      dataType="str"
                      length="50"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[order_id]"
                      name="order_id" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[order_item_id]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[order_item_id]"
                      name="order_item_id" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[CustomerSK]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[CustomerSK]"
                      name="CustomerSK" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ProductSK]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ProductSK]"
                      name="ProductSK" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[SellerSK]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[SellerSK]"
                      name="SellerSK" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[DateKey]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[DateKey]"
                      name="DateKey" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[price]"
                      dataType="numeric"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[price]"
                      name="price"
                      precision="18"
                      scale="2" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[freight_value]"
                      dataType="numeric"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[freight_value]"
                      name="freight_value"
                      precision="18"
                      scale="2" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[TotalOrderValue]"
                      dataType="numeric"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[TotalOrderValue]"
                      name="TotalOrderValue"
                      precision="18"
                      scale="2" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[DeliveryTimeDays]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[DeliveryTimeDays]"
                      name="DeliveryTimeDays" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Fact_Orders\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Loads completed orders into Fact_Orders"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="The number of seconds before a command times out.  A value of 0 indicates an infinite time-out." name="CommandTimeout">0</property>
                <property dataType="System.String" description="Specifies the name of the database object used to open a rowset." name="OpenRowset">[dbo].[Fact_Orders]</property>
                <property dataType="System.String" description="Specifies the variable that contains the name of the database object used to open a rowset." name="OpenRowsetVariable"></property>
                <property dataType="System.String" description="The SQL command to be executed." name="SqlCommand" UITypeEditor="Microsoft.DataTransformationServices.Controls.ModalMultilineStringEditor"></property>
                <property dataType="System.Int32" description="Specifies the column code page to use when code page information is unavailable from the data source." name="DefaultCodePage">1252</property>
                <property dataType="System.Boolean" description="Forces the use of the DefaultCodePage property value when describing character data." name="AlwaysUseDefaultCodePage">false</property>
                <property dataType="System.Int32" description="Specifies the mode used to access the database." name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="Indicates whether the values supplied for identity columns will be copied to the destination." name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="Indicates whether the columns containing null will have null inserted in the destination." name="FastLoadKeepNulls">false</property>
                <property dataType="System.String" description="Specifies options to be used with fast load." name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
                <property dataType="System.Int32" description="Specifies when commits are issued during data insertion." name="FastLoadMaxInsertCommitSize">2147483647</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  description="The OLE DB runtime connection used to access the database."
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <inputColumns>
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[order_id]"
                      cachedCodepage="1252"
                      cachedDataType="str"
                      cachedLength="50"
                      cachedName="order_id"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[OrderBK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[order_id]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[order_item_id]"
                      cachedDataType="i4"
                      cachedName="order_item_id"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[OrderItemBK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[order_item_id]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[CustomerSK]"
                      cachedDataType="i4"
                      cachedName="CustomerSK"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerSK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[CustomerSK]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[ProductSK]"
                      cachedDataType="i4"
                      cachedName="ProductSK"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductSK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[ProductSK]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[SellerSK]"
                      cachedDataType="i4"
                      cachedName="SellerSK"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerSK]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[SellerSK]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[DateKey]"
                      cachedDataType="i4"
                      cachedName="DateKey"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[DateKey]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[DateKey]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[price]"
                      cachedDataType="numeric"
                      cachedName="price"
                      cachedPrecision="18"
                      cachedScale="2"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[Price]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[price]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[freight_value]"
                      cachedDataType="numeric"
                      cachedName="freight_value"
                      cachedPrecision="18"
                      cachedScale="2"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[FreightValue]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[freight_value]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[TotalOrderValue]"
                      cachedDataType="numeric"
                      cachedName="TotalOrderValue"
                      cachedPrecision="18"
                      cachedScale="2"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[TotalOrderValue]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[TotalOrderValue]" />
                    <inputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].Columns[DeliveryTimeDays]"
                      cachedDataType="i4"
                      cachedName="DeliveryTimeDays"
                      externalMetadataColumnId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[DeliveryTimeDays]"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output].Columns[DeliveryTimeDays]" />
                  </inputColumns>
                  <externalMetadataColumns isUsed="True">
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[OrderBK]"
                      codePage="1252"
                      dataType="str"
                      length="64"
                      name="OrderBK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[OrderItemBK]"
                      dataType="i4"
                      name="OrderItemBK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[CustomerSK]"
                      dataType="i4"
                      name="CustomerSK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[ProductSK]"
                      dataType="i4"
                      name="ProductSK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[SellerSK]"
                      dataType="i4"
                      name="SellerSK" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[DateKey]"
                      dataType="i4"
                      name="DateKey" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[Price]"
                      dataType="numeric"
                      name="Price"
                      precision="18"
                      scale="2" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[FreightValue]"
                      dataType="numeric"
                      name="FreightValue"
                      precision="18"
                      scale="2" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[TotalOrderValue]"
                      dataType="numeric"
                      name="TotalOrderValue"
                      precision="18"
                      scale="2" />
                    <externalMetadataColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input].ExternalColumns[DeliveryTimeDays]"
                      dataType="i4"
                      name="DeliveryTimeDays" />
                  </externalMetadataColumns>
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Fact_Orders\\OLE DB Destination.Outputs[OLE DB Destination Error Output]"
                  exclusionGroup="1"
                  isErrorOut="true"
                  name="OLE DB Destination Error Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input]">
                  <outputColumns>
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorCode]"
                      name="ErrorCode"
                      specialFlags="1" />
                    <outputColumn
                      refId="Package\\Load_Fact_Orders\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      dataType="i4"
                      lineageId="Package\\Load_Fact_Orders\\OLE DB Destination.Outputs[OLE DB Destination Error Output].Columns[ErrorColumn]"
                      name="ErrorColumn"
                      specialFlags="2" />
                  </outputColumns>
                  <externalMetadataColumns />
                </output>
              </outputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Fact_Orders.Paths[OLE DB Source Output]"
              endId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="OLE DB Source Output"
              startId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>
  </DTS:Executables>
  <DTS:PrecedenceConstraints>
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Prepare_to_Customer]"
      DTS:CreationName=""
      DTS:DTSID="{C11AA4B6-BB54-7BBC-D665-9D481BA5C411}"
      DTS:From="Package\\Prepare_DW_Tables"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Prepare_to_Customer"
      DTS:To="Package\\Load_Dim_Customer" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Customer_to_Product]"
      DTS:CreationName=""
      DTS:DTSID="{D57EA4B6-BB54-7BBC-D665-9D481BA5C423}"
      DTS:From="Package\\Load_Dim_Customer"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Customer_to_Product"
      DTS:To="Package\\Load_Dim_Product" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Product_to_Seller]"
      DTS:CreationName=""
      DTS:DTSID="{B718D934-C82E-44F1-8A1C-8A97F2491A23}"
      DTS:From="Package\\Load_Dim_Product"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Product_to_Seller"
      DTS:To="Package\\Load_Dim_Seller" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Seller_to_Date]"
      DTS:CreationName=""
      DTS:DTSID="{E827B134-8A3F-4189-9A8C-3B4791E47A55}"
      DTS:From="Package\\Load_Dim_Seller"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Seller_to_Date"
      DTS:To="Package\\Load_Dim_Date" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Date_to_Fact]"
      DTS:CreationName=""
      DTS:DTSID="{E68FB5C7-CC65-8CCD-E776-AE592CB6D534}"
      DTS:From="Package\\Load_Dim_Date"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Date_to_Fact"
      DTS:To="Package\\Load_Fact_Orders" />
  </DTS:PrecedenceConstraints>
  <DTS:DesignTimeProperties><![CDATA[<?xml version="1.0"?>
<Objects
  Version="8">
  <Package
    design-time-name="Package">
    <LayoutInfo>
      <GraphLayout
        Capacity="16" xmlns="clr-namespace:Microsoft.SqlServer.IntegrationServices.Designer.Model.Serialization;assembly=Microsoft.SqlServer.IntegrationServices.Graph" xmlns:mssgle="clr-namespace:Microsoft.SqlServer.Graph.LayoutEngine;assembly=Microsoft.SqlServer.Graph" xmlns:assembly="http://schemas.microsoft.com/winfx/2006/xaml">
        <NodeLayout
          Size="180,42"
          Id="Package\\Prepare_DW_Tables"
          TopLeft="100,30" />
        <NodeLayout
          Size="180,42"
          Id="Package\\Load_Dim_Customer"
          TopLeft="100,110" />
        <NodeLayout
          Size="180,42"
          Id="Package\\Load_Dim_Product"
          TopLeft="100,190" />
        <NodeLayout
          Size="180,42"
          Id="Package\\Load_Dim_Seller"
          TopLeft="100,270" />
        <NodeLayout
          Size="180,42"
          Id="Package\\Load_Dim_Date"
          TopLeft="100,350" />
        <NodeLayout
          Size="180,42"
          Id="Package\\Load_Fact_Orders"
          TopLeft="100,430" />
        <EdgeLayout
          Id="Package.PrecedenceConstraints[Constraint_Prepare_to_Customer]"
          TopLeft="190,72">
          <EdgeLayout.Curve>
            <mssgle:Curve
              StartConnector="{assembly:Null}"
              EndConnector="0,38"
              Start="0,0"
              End="0,30.5">
              <mssgle:Curve.Segments>
                <mssgle:SegmentCollection
                  Capacity="5">
                  <mssgle:LineSegment
                    End="0,30.5" />
                </mssgle:SegmentCollection>
              </mssgle:Curve.Segments>
            </mssgle:Curve>
          </EdgeLayout.Curve>
          <EdgeLayout.Labels>
            <EdgeLabelCollection />
          </EdgeLayout.Labels>
        </EdgeLayout>
        <EdgeLayout
          Id="Package.PrecedenceConstraints[Constraint_Customer_to_Product]"
          TopLeft="190,152">
          <EdgeLayout.Curve>
            <mssgle:Curve
              StartConnector="{assembly:Null}"
              EndConnector="0,38"
              Start="0,0"
              End="0,30.5">
              <mssgle:Curve.Segments>
                <mssgle:SegmentCollection
                  Capacity="5">
                  <mssgle:LineSegment
                    End="0,30.5" />
                </mssgle:SegmentCollection>
              </mssgle:Curve.Segments>
            </mssgle:Curve>
          </EdgeLayout.Curve>
          <EdgeLayout.Labels>
            <EdgeLabelCollection />
          </EdgeLayout.Labels>
        </EdgeLayout>
        <EdgeLayout
          Id="Package.PrecedenceConstraints[Constraint_Product_to_Seller]"
          TopLeft="190,232">
          <EdgeLayout.Curve>
            <mssgle:Curve
              StartConnector="{assembly:Null}"
              EndConnector="0,38"
              Start="0,0"
              End="0,30.5">
              <mssgle:Curve.Segments>
                <mssgle:SegmentCollection
                  Capacity="5">
                  <mssgle:LineSegment
                    End="0,30.5" />
                </mssgle:SegmentCollection>
              </mssgle:Curve.Segments>
            </mssgle:Curve>
          </EdgeLayout.Curve>
          <EdgeLayout.Labels>
            <EdgeLabelCollection />
          </EdgeLayout.Labels>
        </EdgeLayout>
        <EdgeLayout
          Id="Package.PrecedenceConstraints[Constraint_Seller_to_Date]"
          TopLeft="190,312">
          <EdgeLayout.Curve>
            <mssgle:Curve
              StartConnector="{assembly:Null}"
              EndConnector="0,38"
              Start="0,0"
              End="0,30.5">
              <mssgle:Curve.Segments>
                <mssgle:SegmentCollection
                  Capacity="5">
                  <mssgle:LineSegment
                    End="0,30.5" />
                </mssgle:SegmentCollection>
              </mssgle:Curve.Segments>
            </mssgle:Curve>
          </EdgeLayout.Curve>
          <EdgeLayout.Labels>
            <EdgeLabelCollection />
          </EdgeLayout.Labels>
        </EdgeLayout>
        <EdgeLayout
          Id="Package.PrecedenceConstraints[Constraint_Date_to_Fact]"
          TopLeft="190,392">
          <EdgeLayout.Curve>
            <mssgle:Curve
              StartConnector="{assembly:Null}"
              EndConnector="0,38"
              Start="0,0"
              End="0,30.5">
              <mssgle:Curve.Segments>
                <mssgle:SegmentCollection
                  Capacity="5">
                  <mssgle:LineSegment
                    End="0,30.5" />
                </mssgle:SegmentCollection>
              </mssgle:Curve.Segments>
            </mssgle:Curve>
          </EdgeLayout.Curve>
          <EdgeLayout.Labels>
            <EdgeLabelCollection />
          </EdgeLayout.Labels>
        </EdgeLayout>
      </GraphLayout>
    </LayoutInfo>
  </Package>
</Objects>]]></DTS:DesignTimeProperties>
</DTS:Executable>
"""

with open(r"ssis\Olist_ETL\Package.dtsx", "w", encoding="utf-8") as f:
    f.write(package_xml.strip())

print("Successfully generated all-inclusive 6-task Package.dtsx!")
