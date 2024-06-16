# Maple

## Automate your model Quality Check with Speckle and Maple

### About

Maple is a library designed to write simple code that can check
different attributes of a Model in Speckle.

Using Maple you can write `test specs` that check any parameter
or quantity inside the project model.

Maple can be integrated into [Speckle Automate](https://speckle.systems/blog/automate-with-speckle/)
to run the quality check tests on a continuous integration and ensure project standards.
See [Maple-Automate-CI](https://github.com/Gizemdem/Mapple-CI-Pipeline) to check the full implementation of maple in Speckle Automate.

### Get started

Install the library from PyPi

```sh
pip install maple-spec
```

Then, create your `main.py` to test your specs locally

```py
# main.py
import maple as mp

def spec_a():
    mp.it("checks window height is greater than 2600 mm")

    mp.get('category', 'Windows')\
        .where('speckle_type',
               'Objects.Other.Instance:Objects.Other.Revit.RevitInstance')\
        .its('Height')\
        .should('be.greater', 2600)

# Use the stream id of one of your projects
mp.stream("streamid")
mp.run(spec_a)
```
For this to work out of the box, you should have the [Speckle Manager](https://speckle.systems/download/)
installed and your account set-up, so Maple can fetch the data from your `stream`.

If not, alternatively you can set an environment variable called `SPECKLE_TOKEN` with a Speckle token that can read from streams, for example:

```sh
SPECKLE_TOKEN="your-secret-token"
```

Finally run the file with python like so:

```sh
python main.py
```

