#include "snowboy-io.h"

std::string snowboy::DecryptString(const std::string &input) {
  std::string tmp_string = input;

  snowboy::EncryptToken(&tmp_string);

  return tmp_string;
}
