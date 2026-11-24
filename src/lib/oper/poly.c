float
Poly3 (const float x,
       const float Coefs[])
{
  return (Coefs[0] + x * (Coefs[1] + x * (Coefs[2] + x * Coefs[3])));
}

float
Poly1 (const float x,
       const float Coefs[])
{
  return (Coefs[0] + x * Coefs[1]);
}

float
Poly11 (const float x,
	const float y,
	const float Coefs[])
{
  return (Coefs[0] + x * Coefs[1] + y * Coefs[2]);
}
