typedef struct
{
  float decal;
  unsigned long nb_decal_OK;
  unsigned long nb_GPS_time_mnq;
} CR_conv_GPS_time_t;

#define GPS_UTC_OK  0
#define GPS_UTC_MULTI  -1
#define GPS_UTC_NOTFOUND  -2

