# Hentavfall

Support for schedules provided by [Hentavfall](https://www.hentavfall.no), serving Multiple, Norway.

## Configuration via configuration.yaml

```yaml
waste_collection_schedule:
    sources:
    - name: hentavall_no
      args:
        id: ID
        municipality: municipality
        gnumber: "gnumber"
        bnumber: "bnumber"
        snumber: "snumber"
        
```

### Configuration Variables

**id**  
*(String | Integer) (required)*

**municipality**  
*(String) (required)*

**gnumber**  
*(String | Integer) (required)*

**bnumber**  
*(String | Integer) (required)*

**snumber**  
*(String | Integer) (required)*

## Example

```yaml
waste_collection_schedule:
    sources:
    - name: hentavall_no
      args:
        id: 181e5aac-3c88-4b0b-ad46-3bd246c2be2c
        municipality: Sandnes
        gnumber: "62"
        bnumber: "281"
        snumber: "0"
        
```

## How to get the source argument

Find the parameter of your address using [https://www.hentavfall.no/rogaland/sandnes/tommekalender/](https://www.hentavfall.no/rogaland/sandnes/tommekalender/) and write them exactly like on the web page.
