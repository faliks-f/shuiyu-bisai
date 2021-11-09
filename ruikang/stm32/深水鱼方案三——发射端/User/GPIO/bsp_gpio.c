#include "bsp_GPIO.h"

/*name
GPIOA
GPIOB
GPIOC
GPIOD
GPIOE
GPIOF
GPIOG*/

/*add
0~15
*/

/*mode
GPIO_Mode_AIN
GPIO_Mode_IN_FLOATING
GPIO_Mode_IPD
GPIO_Mode_IPU
GPIO_Mode_Out_OD
GPIO_Mode_Out_PP
GPIO_Mode_AF_OD
GPIO_Mode_AF_PP
*/

/**名称：初始化GPIO
	*功能：开启相关时钟
	*/
void GPIO_Config(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA|RCC_APB2Periph_GPIOB|RCC_APB2Periph_GPIOC,ENABLE);
}

/**名称：GPIO输出
	*功能：使对应引脚输出对应电平
	*/
void GPIO_Out(GPIO_TypeDef* name,uint8_t add,GPIOMode_TypeDef mode,uint8_t valid)
{
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0<<add;
	GPIO_InitStructure.GPIO_Mode = mode;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(name, &GPIO_InitStructure);
	if(valid) GPIO_SetBits(name,GPIO_Pin_0<<add);
	else GPIO_ResetBits(name,GPIO_Pin_0<<add);
}

/**名称：GPIO输入
	*功能：读取对应引脚电平
	*/
uint8_t GPIO_Read(GPIO_TypeDef* name,uint8_t add,GPIOMode_TypeDef mode)
{
	GPIO_InitTypeDef GPIO_InitStructure;
	/*选择需要控制的GPIO引脚*/
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0<<add;
	GPIO_InitStructure.GPIO_Mode = mode; 
	GPIO_Init(name,&GPIO_InitStructure);
	return GPIO_ReadInputDataBit(name,GPIO_Pin_0<<add);
}
