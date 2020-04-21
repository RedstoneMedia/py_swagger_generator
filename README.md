# Python Swagger Generator v.1.0.4

This is a package for python to automatically create swagger documentation yaml files using templates.

## Installation
Install this package using pip :
`pip install py-swagger-generator`


## Usage

After installing this package you can execute the tool in the terminal by typing
`py-swagger-generator`

This command currently has 2 arguments :
- --verbose : Outputs some more debug information
- -r        : Inserts the generated swagger yaml under the routes in the selected document
- -d        : Specify the input document file over the command line arguments
- td        : Specify the input template file over the command line arguments

After specifying your options the tool will ask you which swagger document file you want to target.\
It will also aks you to input the path of the template you wan't to use to create your new data.

After you entered all that, the program will ask you questions depending on the template you selected, to fill in the fields in the template.

### Templates

A Template is in our case just a normal yaml file with some modifications.

These modifications start whenever the program sees two `{` characters and ends when it sees two `}` characters.

These modifications tell our program what to ask the user and will be replaced with what the user has inputted in that specific field.

Every modification has some arguments some are required some are not.
Arguments are separated using commas.
Its important that the arguments are in a specific order since the meaning of the date inside a argument changes based on its order.

The argument order is as follows :

| Argument Index | Argument Name  | Required                              | Default Value | Format                                                                                                                                                                                                | Argument Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------|:---------------|:--------------------------------------|:--------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0              | Key Name       | yes                                   | -             | At least one character. All uppercase and `_`                                                                                                                                                         | This argument will be used to identify the argument and is also the name that will be displayed when the program is asking the user for a value in a template.                                                                                                                                                                                                                                                                                                                               |
| 1              | Input Type     | yes                                   | -             | `STRING`, `INTEGER`, `SCHEMA`, `OBJECT` `CHOOSE_ONE< Insert data type here >( Choices separated by the pipe character` `CHOOSE_ANY Then same as choose one` `CHOOSE_ANY_LIST Then same as choose one` | The type of the value you want to ask the user for. If set to `CHOOSE_ONE` the user can choose from a list of values that you provide in the template inside the parentheses right after the choice data type, which will then be converted to the type you specify in the angle brackets. If set to `CHOOSE_ANY` its the same as `CHOSE_ONE`, but you can select more then one item. Setting it to `CHOOSE_ANY_LIST` dose the same as `CHOSE_ANY`, but the generated is inserted as a list. |
| 2              | Is Required    | only if input type is set to `OBJECT` | REQUIRED      | `REQUIRED`, `OPTIONAL`                                                                                                                                                                                | Indicates if the user has to enter the value or not. If set to `OPTIONAL` the user will be asked if he wants to enter the value.                                                                                                                                                                                                                                                                                                                                                             |
| 3              | Multiple Type  | only if input type is set to `OBJECT` | SINGLE        | `SINGLE`, `ONE_OR_MORE`, `ONE_OR_MORE_LIST`                                                                                                                                                           | Indicates how many times the user can enter the value. It can only be set to `ONE_OR_MORE` or `ONE_OR_MORE_LIST` if the input type is set to `OBJECT`. If set to `ONE_OR_MORE` the user will be asked to enter all the values in the reference object at least once and will then be asked if he would like to add another object. `ONE_OR_MORE_LIST` has the same functionality as `ONE_OR_MORE`, however the object will be inserted as a list in the generated yaml.                      |
| 4              | Reference Path | only if input type is set to `OBJECT` | -             | Anny characters followed by .yaml                                                                                                                                                                     | This argument contains the path to another template. This argument can only be set if the input type is set to `OBJECT`. If the program encounters this value it will interpret the argument as a path and interpret the file at the path as template. It will ask the user for all values that the referenced template includes and will then insert the filled yaml of the referenced template.                                                                                            |

Here is a example for a really simple route template which could be stored under `templates/route.yaml` :

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
      {{RESPONSE, OBJECT, REQUIRED, ONE_OR_MORE, templates/response.yaml}}
```

You can see that this templates references to `templates/response.yaml` which content could be seen here :

```yaml
'{{STATUS_CODE, INTEGER, REQUIRED}}':
  description: {{DESCRIPTION, STRING, REQUIRED}}
```