#ifndef __BSP_GPIO_H
#define __BSP_GPIO_H

#include "stm32f10x.h"

void GPIO_Config(void);
void GPIO_Out(GPIO_TypeDef* name,uint8_t add,GPIOMode_TypeDef mode,uint8_t valid);
uint8_t GPIO_Read(GPIO_TypeDef* name,uint8_t add,GPIOMode_TypeDef mode);

#endif /*__BSP_GPIO_H*/
