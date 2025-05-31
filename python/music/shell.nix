{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python310.withPackages (ps: with ps; [
    aiohttp
    pygame
    pyserial
  ]);
in

pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.alsa-lib  # For libasound.so.2 (needed by pygame)
  ];

}
