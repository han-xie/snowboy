#ifndef SNOWBOY_IO_H_
#define SNOWBOY_IO_H_

#include <string>

namespace snowboy {

void EncryptToken(std::string *input);

std::string DecryptString(const std::string &input);

}  // end namespace snowboy

#endif  // SNOWBOY_IO_H_

