# Python Swagger Generator v.1.1.0

This is a package for python to automatically create swagger documentation yaml files using templates.

## Installation
Install this package using pip :
`pip install py-swagger-generator`


## Usage

After installing this package you can execute the tool in the terminal by typing
`py-swagger-generator`

This command currently has 2 arguments :
- --verbose : Outputs some more debug information
- --build   : Builds everything inside the swagger_generator folder.

### Config Folders

A config folder is a folder inside the `swagger_generator` folder that contains a `config.yaml` file and a `templates` folder (This is where you place your template files).

There can be more than one config folder inside the swagger_generator folder.

The structure of the config.yaml is as follows :

```yaml
data:
  routes:
    - [Name of template without .yaml and containing data for the Route]
    
  components:
    responses:
    - [Name of template without .yaml and containing data for the Response]
      
    schemas:
    - [Name of template without .yaml and containing data for the Schema]
      

build:
  output: [Path to Where the finished result will be stored at]
```

If you put any data that dose not fall under the keys named above under the `data` key, then this data will not be modified, but will be placed inside the output file.

### Templates

A Template is in our case just a normal yaml file with some modifications.

These modifications start whenever the program sees two `{` characters and ends when it sees two `}` characters.

These modifications will be replaced with what the user has inputted in that specific field in the config.yaml file.

Every modification has some arguments some are required some are not.
Arguments are separated using commas.
Its important that the arguments are in a specific order since the meaning of the data inside a argument changes based on its order.

The argument order is as follows :

| Argument Index | Argument Name  | Required                              | Default Value | Format                                                                                                                                                                                                  | Argument Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------|:---------------|:--------------------------------------|:--------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0              | Key Name       | yes                                   | -             | At least one character. All uppercase and `_`                                                                                                                                                           | This argument will be used to identify the argument and is also the name that will be displayed when the program is asking the user for a value in a template.                                                                                                                                                                                                                                                                                                                               |
| 1              | Input Type     | yes                                   | -             | `STRING`, `INTEGER`, `SCHEMA`, `OBJECT` `CHOOSE_ONE< Insert data type here >( Choices separated by the pipe character )` `CHOOSE_ANY Then same as choose one` `CHOOSE_ANY_LIST Then same as choose one` | The type of the value you want to ask the user for. If set to `CHOOSE_ONE` the user can choose from a list of values that you provide in the template inside the parentheses right after the choice data type, which will then be converted to the type you specify in the angle brackets. If set to `CHOOSE_ANY` its the same as `CHOSE_ONE`, but you can select more then one item. Setting it to `CHOOSE_ANY_LIST` dose the same as `CHOSE_ANY`, but the generated is inserted as a list. |
| 2              | Is Required    | only if input type is set to `OBJECT` | REQUIRED      | `REQUIRED`, `OPTIONAL`                                                                                                                                                                                  | Indicates if the user has to provide the value or not.                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 3              | Multiple Type  | only if input type is set to `OBJECT` | SINGLE        | `SINGLE`, `ONE_OR_MORE`, `ONE_OR_MORE_LIST`                                                                                                                                                             | Indicates how many times the user can enter the value. It can only be set to `ONE_OR_MORE` or `ONE_OR_MORE_LIST` if the input type is set to `OBJECT`. If set to `ONE_OR_MORE` the user will need to enter all the values in the reference object. `ONE_OR_MORE_LIST` has the same functionality as `ONE_OR_MORE`, however the object will be inserted as a list in the generated yaml.                                                                                                      |
| 4              | Reference Path | only if input type is set to `OBJECT` | -             | Any characters followed by .yaml                                                                                                                                                                        | This argument contains the path to another template. This argument can only be set if the input type is set to `OBJECT`. If the program encounters this value it will interpret the argument as a path and interpret the file at that path as template. The user will have to provide all values that the referenced template includes and the program will then insert the filled yaml of the referenced template at that point.                                                            |

### Example

Here is a example for a really simple route template which could be stored under `swagger_generator/test_config/templates/route.yaml` :

```yaml
/{{ROUTE_PATH, STRING, REQUIRED}}:
  {{HTML_REQUEST_TYPE, STRING, REQUIRED}}:
    tags:
    - {{CATORGY, STRING, REQUIRED}}
    summary: {{SUMMARY, STRING, REQUIRED}}
    operationId: {{OPERATION_ID, STRING, REQUIRED}}
    requestBody:
      content:
        application/json:
          schema:
            {{SCHEMA, SCHEMA, REQUIRED}}
    responses:
      {{RESPONSE, OBJECT, REQUIRED, ONE_OR_MORE, response.yaml}}
```

You can see that this templates references to `swagger_generator/test_config/templates/response.yaml` which content could be seen here :

```yaml
'{{STATUS_CODE, INTEGER, REQUIRED}}':
  description: {{DESCRIPTION, STRING, REQUIRED}}
```

Now we only need to create a `config.yaml` file for our test_config which could be stored here : `swagger_generator/test_config/config.yaml`

```yaml
data:
  openapi: 3.0.1
  info:
    title: Test
    version: v1
    - url: http://localhost:80
  tags:
    - name: test
      description: Test
  routes:
    - route:
        ROUTE_PATH: test
        HTML_REQUEST_TYPE: post
        CATORGY: test
        SUMMARY: Dose some stuff and things.
        OPERATION_ID: test
        SCHEMA:
          name:
            type: string
          data:
            type: string
        RESPONSE:
          - STATUS_CODE: 200
            DESCRIPTION: Ok

build:
  output: test.yaml
```

Now just call `py-swagger-generator --build`.
This will generate a test.yaml file containing all the specified data.