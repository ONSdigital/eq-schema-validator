const Ajv = require('ajv');
const axios = require('axios');
const fs = require('fs');
const glob = require('glob');
const express = require("express");
const app = express();

let ajv = new Ajv({
  meta: false,
  extendRefs: true,
  unknownFormats: 'ignore',
  allErrors: false,
  schemaId: 'auto'
});
ajv.addMetaSchema(require('ajv/lib/refs/json-schema-draft-07.json'));

app.use(express.json({
  'limit': '2Mb'
}));

app.listen(5001, () => {
  console.log("Server running on port 5001");
});

app.get("/status", (req, res, next) => {
    return res.sendStatus(200);
});

glob("../schemas/**/*.json", function (er, schemas) {
  schemas.forEach((currentSchema) => {
    let data = fs.readFileSync(currentSchema);
    ajv.addSchema(JSON.parse(data));
  });

  var validate = ajv.compile(require('../schemas/questionnaire_v1.json'));

  app.post("/validate", (req, res, next) => {
    let valid = validate(req.body);
    console.log("Validating questionnaire: " + req.body['title']);
    if (!valid) {
      return res.json({'success': false, 'errors': validate.errors.sort((a, b) => {
        return b.dataPath.length - a.dataPath.length;
      })})
    }
    return res.json({})
  });
});