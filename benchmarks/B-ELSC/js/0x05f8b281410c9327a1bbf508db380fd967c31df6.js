var contract = artifacts.require("MyAdvancedToken");

module.exports = function(deployer) {
  deployer.deploy(contract, 1000000, "TOK", "TOK");
};
